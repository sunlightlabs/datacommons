import re
import os
import time
import datetime
import traceback

from django.core.management.base import BaseCommand
from django.conf import settings

from dcentity.tools.models import EntityPlus
from dcentity.tools import wpapi
from dcentity.tools.names import PersonName, OrganizationName
from dcentity.tools import utils

def find_wikipedia_url(entity):
    """
    Returns a tuple of (url, article excerpt, image url) for a given entity, or None if no
    matching article is found.
    """
    empty_result = ['', '']
    if entity.type == 'individual':
        return empty_result

    for ename in entity.names:
        # Search for exact title matches with redirects.  Use for comparing
        # titles later -- we might exactly match a redirect title, but not
        # match the destination page at all.  Full text search returns only
        # the destination pages, not the redirections.
        redirects = wpapi.title_search_redirects(ename.search_string()) 

        # Full text search!
        results = wpapi.full_text_search(entity.get_search_terms(ename))
        for result in results:
            article = wpapi.WikipediaArticle(result['title'])
            # Exclude special namespaced articles (e.g. User:, Template:,
            # etc.)
            if (article.namespace or article.title.startswith("List of") or
                    article.is_disambiguation_page()):
                continue

            if article.title in redirects:
                name_comp = wpapi.WikipediaArticle(redirects.get(article.title)).name
            else:
                name_comp = article.name

            if entity.type == 'politician':
                if ename != PersonName(name_comp):
                    continue
                if not article.is_politician():
                    continue
                if not article.is_american():
                    continue
                subject = article.get_subject()
                if subject and ename != PersonName(article.get_subject()):
                    continue

            elif entity.type == 'organization':
                if ename.is_politician():
                    if ename.pname != PersonName(name_comp):
                        continue
                    if not article.is_politician():
                        continue
                    if not article.is_american():
                        continue
                else:
                    if ename != OrganizationName(name_comp):
                        continue
                    if article.is_person():
                        continue
                    if ename.is_company() and not article.is_company():
                        continue
            wikipedia_url = wpapi.article_url(article.title)
            wikipedia_excerpt = wpapi.get_article_excerpt(article.title)
            return (wikipedia_url, wikipedia_excerpt)
    return empty_result

class Command(BaseCommand):
    args = '<output_file>'
    help = """Fetch wikipedia matches for all entities.  Requires one argument,
<output_file>, which is a CSV file to which results will be written.  The
results will include:

    entity_id, wikipedia_url or '', wikipedia_excerpt or '', datetime of fetch
    
Entries are not overridden -- if the file already contains a match for a given
entity_id, it will not be re-queried.  It should thus be efficient to restart
the process.  If you wish to refresh an entity, delete the row or start with a
fresh file.

If errors are encountered during the scrape (which may take as long as 48 hours
to complete), the error messages are written to a file named
`<output_file>.errors.csv`.  To retry the entries that encountered errors, use
the `./manage.py entity_wikipedia_error_recovery` command which reads the error
file.  See that command for more details.

Please note: This management command uses memcached to cache all communication
with wikipedia to speed the process. If HTTP errors are encountered during a
scrape, it may be necessary to clear the cache in order to retry them.  This
can be accomplished from the Django shell like so:
    $ python manage.py shell
    >>> from django.core.cache import cache
    >>> cache.clear()
"""

    def handle(self, *args, **kwargs):
        if len(args) < 1:
            print "Requires one argument: <output_file>"
            print
            print self.help
            return
        output_file = args[0]
        error_file = "%s.errors%s" % os.path.splitext(output_file)

        # Fetch and record new results
        with utils.reopen_csv_writer(output_file) as (rows, writer):
            self.results = dict((row[0], row) for row in rows)
            self.writer = writer
            with utils.reopen_csv_writer(error_file) as (rows, error_writer):
                self.errors = dict((row[0], row) for row in rows)
                self.error_writer = error_writer

                qs = EntityPlus.objects.exclude(type='individual')
                total = qs.count()
                # This'll take up to 48 hours
                for c, entity in enumerate(qs):
                    self._fetch_one(entity, c, total)
            
            # Retry errors once; most of the time it's just an HTTP error
            # thrown by wikipedia.
            with open(error_file, 'w') as error_fh:
                # We now have a blank error file.
                self.error_writer = utils.UnicodeWriter(error_fh)
                for eid, row in self.errors.items():
                    try:
                        entity = EntityPlus.objects.get(id=eid)
                        # Recurring errors in self._fetch_one are caught inside
                        # and re-logged.
                        self._fetch_one(entity, c, total)
                        del self.errors[eid]
                    except Exception:
                        # Failsafe in case we get a database read error or
                        # something.
                        self._log_error(row)
            if not self.errors:
                # Get rid of the noise
                os.remove(error_file)

    def _fetch_one(self, entity, c=0, total=0):
        if entity.id in self.results:
            return

        start = time.time()
        try:
            url, excerpt = find_wikipedia_url(entity)
        except Exception as e:
            print "EXCEPTION", traceback.format_exc()
            row = (entity.id, entity.names[0].name, str(e.args), traceback.format_exc())
            self._log_error(row)
        else:
            row = (entity.id, url, excerpt, unicode(datetime.datetime.now()))
            self.results[row[0]] = row
            self.writer.writerow(row)
            print "%i/%i" % (c, total), (entity.names[0].name, url), \
                "time:", "%.02f" % (time.time()-start), "seconds"

    def _log_error(self, row):
        self.error_writer.writerow(row)
        self.errors[row[0]] = row
