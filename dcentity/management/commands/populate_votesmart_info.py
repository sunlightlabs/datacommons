import urllib, urllib2, logging, pprint, pickle, os

from django.conf                 import settings
from django.core.management.base import BaseCommand
from django.db                   import connection, transaction
from name_cleaver.name_cleaver   import PoliticianNameCleaver, RunningMatesNames
from votesmart                   import votesmart, VotesmartApiError

try:
    import json
except:
    import simplejson as json

class Command(BaseCommand):
    args = '<limit> <offset (optional)>'

    help = 'Populate VoteSmart info'

    no_match = []
    too_many = []

    def __init__(self):
        self.set_up_logger()
        votesmart.apikey = '52b1e53c3d62bf531e8dd482067d043a'
        self.pp = pprint.PrettyPrinter(width=50)

        self.office_id_map = {
            'state:governor': [3,4],
            'federal:house': [5],
            'federal:senate': [6],
        }


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

        #candidates = self.get_all_congressional_candidates()
        #self.candidates = self.filter_candidates(candidates)

        cursor = connection.cursor()

        # get count
        cursor.execute("select count(*) from politician_metadata_latest_cycle_view")
        total = cursor.fetchone()
        transaction.rollback()

        select_sql = """
            select entity_id, name, state, district, seat, cycle
            from politician_metadata_latest_cycle_view m
            inner join matchbox_entity e on e.id = m.entity_id
            where
                entity_id not in (select entity_id from matchbox_votesmartinfo)
                and seat in ('state:governor', 'federal:house', 'federal:senate')
            order by entity_id
        """

        self.log.debug(select_sql)
        cursor.execute(select_sql)
        politicians = cursor.fetchall()
        transaction.rollback()

        self.log.info("{0} federal politicians located to find VoteSmart ids for".format(len(politicians)))

        # Reset existing data
        #cursor.execute("delete from matchbox_votesmartinfo")

        for (entity_id, name, state, district, seat, cycle) in politicians:
            name_obj = PoliticianNameCleaver(name).parse()
            if isinstance(name_obj, RunningMatesNames):
                for mate in name_obj.mates():
                    try:
                        self.process_politician(cursor, entity_id, name, state, district, seat, cycle, mate)
                    except django.db.utils.IntegrityError:
                        continue
            else:
                self.process_politician(cursor, entity_id, name, state, district, seat, cycle, name_obj)

        self.log.info("Done.")
        self.log.info("Names with too many matches:")
        too_many_file = open("/home/akr/work/datacommons/too_many_matches.txt", "w")
        too_many_file.write(self.pp.pformat(self.too_many))
        too_many_file.close()

        self.log.info("Names with no matches:")
        no_match_file = open("/home/akr/work/datacommons/no_match.txt", "w")
        no_match_file.write(self.pp.pformat(self.no_match))
        no_match_file.close()

    def process_politician(self, cursor, entity_id, name, state, district, seat, cycle, name_obj):
        if not district:
            district = ''
        elif '-' in district:
            district = int(district.split('-')[1])

        try:
            candidates = votesmart.candidates.getByLastname(name_obj.last, int(cycle))
        except VotesmartApiError, e:
            return None
            #if e.msg == 'No candidates found matching this criteria.':

        self.log.info("Searching for votesmart id for {0}".format(name))
        votesmart_id = self.get_votesmart_id(candidates, name, state, district, seat)
        if votesmart_id:
            self.log.info("    Found: {0}".format(votesmart_id))

            insert_votesmart_info_sql = """
                insert into matchbox_votesmartinfo (entity_id, votesmart_id) values ('{0}', {1})
            """.format(entity_id, votesmart_id)
            self.log.debug(insert_votesmart_info_sql)
            cursor.execute(insert_votesmart_info_sql)
            transaction.commit()

    def get_all_congressional_candidates(self):
        state_ids = [ x.stateId for x in votesmart.state.getStateIDs() ]
        #self.pp.pprint(state_ids)

        cache_file_size = os.path.getsize("nationwide_candidates.pkl")

        if not cache_file_size:
            cache_file = open("nationwide_candidates.pkl", "w+")
            candidates = {}

            for state in state_ids:
                candidates[state] = {}
                candidates[state]['state:governor'] = []
                try:
                    candidates[state]['state:governor'] = candidates[state]['state:governor'] + votesmart.candidates.getByOfficeState(3, state)
                except VotesmartApiError, e:
                    print "No gubernatorial candidates found in {0}".format(state)

                try:
                    candidates[state]['state:governor'] = candidates[state]['state:governor'] + votesmart.candidates.getByOfficeState(4, state)
                except VotesmartApiError, e:
                    print "No lieutenant gubernatorial candidates found in {0}".format(state)

                try:
                    candidates[state]['federal:house'] = votesmart.candidates.getByOfficeState(5, state)
                except VotesmartApiError, e:
                    print "No congressional candidates found in {0}".format(state)

                try:
                    candidates[state]['federal:senate'] = votesmart.candidates.getByOfficeState(6, state)
                except VotesmartApiError, e:
                    print "No senatorial candidates found in {0}".format(state)

            if len(candidates):
                pickle.dump(candidates, cache_file)

        else:
            cache_file = open("nationwide_candidates.pkl", "r")
            candidates = pickle.load(cache_file)

        cache_file.close()

        return candidates

    def filter_candidates(self, candidates):
        filtered = {}

        for state in candidates.keys():
            for seat in candidates[state].keys():
                if not filtered.has_key(state):
                    filtered[state] = {}

                filtered[state][seat] = candidates[state][seat]
                #filtered[state][seat] = [ x for x in candidates[state][seat] if x.electionStatus not in ['Lost', 'Removed', 'Withdrawn']]
                #filtered[state][seat] = [ x for x in candidates[state][seat] if x.electionStatus == 'Running' ]

        return filtered

    def get_votesmart_id(self, candidates, name, state, district, seat):
        ''' attempt to determine the votesmart_id of this legislator, or return None. '''

        # narrow down by district (if approppriate?)
        #print "{0} {1} {2} {3}".format(name, state, district, seat)
        possibilities = [ x for x in candidates if x.electionDistrictName in [str(district), 'At-Large'] ]

        name_obj = PoliticianNameCleaver(name).parse()

        if isinstance(name_obj, RunningMatesNames):
            name_obj = name_obj.mates()[0] # just use the governor, not lt. governor (this is the only case where it's a list)

        name_possibilities = [ x for x in possibilities if \
                (x.lastName.lower() == name_obj.last.lower() \
                    or (name_obj.middle \
                            and ( \
                                x.lastName.lower() == ' '.join([name_obj.middle.lower(), name_obj.last.lower()]) \
                                or x.lastName.lower() == '-'.join([name_obj.middle.lower(), name_obj.last.lower()]) \
                            )\
                        ) \
                )
                and name_obj.first.lower() in [ x.firstName.lower(), x.preferredName.lower(), x.nickName.lower() ] \
                #and x.electionStatus == 'Running'
                ]

        if len(name_possibilities) == 1:
            cand = name_possibilities[0]
            #if cand.electionStatus == 'Running':
            return cand.candidateId
            #else:
            #    return None
        elif len(name_possibilities) > 1:
            self.too_many.append([(name_obj.first, name_obj.middle, name_obj.last), [ (x.firstName, x.preferredName, x.nickName, x.lastName) for x in possibilities ]])
        else:
            self.no_match.append([(name_obj.first, name_obj.middle, name_obj.last), [ (x.firstName, x.preferredName, x.nickName, x.lastName) for x in possibilities ]])



