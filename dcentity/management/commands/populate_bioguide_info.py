from django.conf                 import settings
from django.core.management.base import BaseCommand
from django.db                   import connections, transaction
from BeautifulSoup               import BeautifulSoup

import urllib
import urllib2
import logging

try:
    import json
except:
    import simplejson as json


class Command(BaseCommand):
    args = '<limit> <offset (optional)>'

    help = 'Populate Bioguide info'

    def __init__(self):
        self.set_up_logger()

    def set_up_logger(self):
        # create logger
        self.log = logging.getLogger("command")
        self.log.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

    @transaction.commit_manually
    def handle(self, *args, **options):
        self.log.info("Starting...")

        # chunk size
        limit = int(args[0]) if args and len(args) else 500
        offset = int(args[1]) if args and len(args) > 1 else 0
        cursor = connections['default'].cursor()

        # get count
        cursor.execute("""
            select
                count(*)
            from
                matchbox_entity e
                inner join politician_metadata_latest_cycle_view pm
                    on e.id = pm.entity_id
            where
                seat like 'federal%%'
        """)
        total = cursor.fetchone()

        transaction.rollback()

        count = 0

        while count < total:
            count += limit

            # loop until we're at the count, doing chunks along the way.

            limit_clause = "limit {0}".format(limit) if limit else ''
            offset_clause = "offset {0}".format(offset) if limit else ''

            select_sql = """
                select
                    entity_id,
                    name,
                    ea.value as crp_id
                from
                    matchbox_entity e
                    inner join politician_metadata_latest_cycle_view pm
                        on e.id = pm.entity_id
                    left join matchbox_entityattribute ea using (entity_id)
                where
                    seat like 'federal%%'
                    and (ea.namespace is null or ea.namespace = 'urn:crp:recipient')
                order by
                    entity_id
                {0}
                {1}
            """.format(limit_clause, offset_clause)

            self.log.debug(select_sql)
            cursor.execute(select_sql)
            politicians = cursor.fetchall()
            transaction.rollback()

            if not len(politicians):
                self.log.info("No more found. Done.")
                return

            # we shouldn't need the offset again in this iteration, so move it over by the amount of the limit
            offset += limit

            self.log.info("Chunk of {0} federal politicians located to find bioguide ids for".format(len(politicians)))

            count_found = 0
            found_ids_and_info = []

            for (entity_id, name, crp_id) in politicians:

                entity = Entity.get(pk=entity_id)

                if hasattr(entity, 'bioguide_info') and entity.bioguide_info.bioguide_id:
                    bioguide_id = entity.bioguide_info.bioguide_id
                else:
                    bioguide_id = self.get_bioguide_id(entity_id)

                if bioguide_id:
                    self.log.info("Found bioguide id for {0}: {1}".format(name, bioguide_id))
                    count_found += 1
                    bioguide_info = self.get_bioguide_info(bioguide_id)
                    if bioguide_info:
                        bio, bio_url, photo_url, years = bioguide_info

                        if len(years) > 32:
                            self.log.warn("Years of service is too long! Value: {0}".format(years))
                            return

                        found_ids_and_info.append((entity_id, bioguide_id, bio, bio_url, photo_url, years))

            self.log.info("Creating temp table tmp_matchbox_bioguideinfo")
            cursor.execute("create temp table tmp_matchbox_bioguideinfo on commit drop as select * from matchbox_bioguideinfo limit 0");


            self.log.info("Inserting into tmp_matchbox_bioguideinfo...")

            values_string = ",".join(["(%s, %s, %s, %s, %s, %s)" for x in found_ids_and_info])
            insert_sql = "insert into tmp_matchbox_bioguideinfo (entity_id, bioguide_id, bio, bio_url, photo_url, years_of_service) values %s" % values_string
            cursor.execute(insert_sql, [item for sublist in found_ids_and_info for item in sublist])

            self.log.info("Finished inserting into temp table. {0} rows inserted.".format(count_found))


            self.log.info("Deleting rows to replace in matchbox_bioguideinfo")
            cursor.execute("""delete from matchbox_bioguideinfo where entity_id in (
                select entity_id from tmp_matchbox_bioguideinfo
            )""")


            self.log.info("Inserting from temp table into real table.")
            cursor.execute("""insert into matchbox_bioguideinfo (entity_id, bioguide_id, bio, bio_url, photo_url, years_of_service)
                select entity_id, bioguide_id, bio, bio_url, photo_url, years_of_service from tmp_matchbox_bioguideinfo""")

            transaction.commit()
            self.log.info('Committed.')

        self.log.info("Done.")

    def get_bioguide_id(self, crp_id):
        ''' attempt to determine the bioguide_id of this legislastor, or
        return None. '''

        arguments = urllib.urlencode({
            'apikey': settings.SYSTEM_API_KEY,
            'crp_id': crp_id,
            'all_legislators': 1,
        })

        url = "http://services.sunlightlabs.com/api/legislators.get.json?"
        api_call = url + arguments

        try:
            fp = urllib2.urlopen(api_call)
        except urllib2.HTTPError:
            return None
        except urllib2.URLError:
            try:
                fp = urllib2.urlopen(api_call)
            except urllib2.URLError:
                self.log.warn('Connection timed out.')
                return None

        js = json.loads(fp.read())

        return js['response']['legislator']['bioguide_id']

    def get_bioguide_info(self, bioguide_id):
        # scrape congress' bioguide site for years of service and official bio
        bio_url = "http://bioguide.congress.gov/scripts/biodisplay.pl?index=%s" % bioguide_id
        print bio_url

        html = urllib2.urlopen(bio_url).read()
        try:
            soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        except ValueError:
            self.log.error("Couldn't parse bioguide info. Sorry. Moving along...")
            return None

        try:
            years_of_service = soup.findAll('table')[1].find('tr').findAll('td')[1].findAll('font')[1].next.strip()

            bio_a = soup.findAll('table')[1].find('tr').findAll('td')[1].find('p').find('font').extract().renderContents()
            bio_b = soup.findAll('table')[1].find('tr').findAll('td')[1].find('p').renderContents()
            biography = bio_a.strip()+' '+bio_b.strip()

            # append additional info and return
            photo_url = self.photo_url(bioguide_id)
            return biography, bio_url, photo_url, years_of_service
        except TypeError:
            self.log.error("Couldn't parse one of the bioguide components from the page. Tough luck, mate. Continuing...")
            return None

    def photo_url(self, bioguide_id):
        return "http://assets.sunlightfoundation.com/moc/100x125/%s.jpg" % bioguide_id if bioguide_id else None

