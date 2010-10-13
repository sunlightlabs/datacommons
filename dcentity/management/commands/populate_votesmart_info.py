import urllib, urllib2, logging, pprint, pickle, os, name_parser

from django.conf                 import settings
from django.core.management.base import BaseCommand
from django.db                   import connection, transaction
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

        candidates = self.get_all_congressional_candidates()
        self.candidates = self.filter_candidates(candidates)

        cursor = connection.cursor()

        # get count
        cursor.execute("select count(*) from matchbox_currentrace cr")
        total = cursor.fetchone()
        transaction.rollback()

        select_sql = """
            select id, name, state, district, seat
            from matchbox_currentrace cr
            order by id
        """

        self.log.debug(select_sql)
        cursor.execute(select_sql)
        politicians = cursor.fetchall()
        transaction.rollback()

        self.log.info("{0} federal politicians located to find VoteSmart ids for".format(len(politicians)))

        cursor.execute("update matchbox_currentrace set election_type = null")
        cursor.execute("delete from matchbox_votesmartinfo")

        for (entity_id, name, state, district, seat) in politicians:
            if '-' in district:
                district = int(district.split('-')[1])

            # we'll only return the ID if the candidate is in the general election
            votesmart_id = self.get_votesmart_id(name, state, district, seat)

            if votesmart_id:
                self.log.info("Found votesmart id for {0}: {1}".format(name, votesmart_id))

                update_currentrace_sql = """
                    update
                        matchbox_currentrace
                    set
                        election_type = 'G'
                    where id = '{0}'
                """.format(entity_id)
                self.log.debug(update_currentrace_sql)
                cursor.execute(update_currentrace_sql)

                insert_votesmart_info_sql = """
                    insert into matchbox_votesmartinfo (entity_id, votesmart_id) values ('{0}', {1})
                """.format(entity_id, votesmart_id)
                self.log.debug(insert_votesmart_info_sql)
                cursor.execute(insert_votesmart_info_sql)

        transaction.commit()

        self.log.info("Done.")
        self.log.info("Names with too many matches:")
        print self.too_many

        self.log.info("Names with no matches:")
        print self.no_match


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

    def get_votesmart_id(self, name, state, district, seat):
        ''' attempt to determine the votesmart_id of this legislator, or return None. '''
        # for governors, we essentially get two names in at this point.
        # let's just go with the first one.

        # get all candidates possible for this seat in this state
        try:
            cands_for_seat = self.candidates[state][seat]
        except:
            #print "No candidates could be found for: {0} {1} {2} {3}".format(name, state, district, seat)
            return None

        # narrow down by district (if approppriate?)
        #print "{0} {1} {2} {3}".format(name, state, district, seat)
        possibilities = [ x for x in cands_for_seat if x.electionDistrictName in [str(district), 'At-Large'] and x.electionStage == 'General' ]

        name_obj = name_parser.standardize_politician_name_to_objs(name)
        if isinstance(name_obj, name_parser.RunningMatesNames):
            name_obj = name_obj.mate1 # just use the governor, not lt. governor (this is the only case where it's a list

        name_possibilities = [ x for x in possibilities if \
                x.lastName.lower() == name_obj.last.lower() \
                and name_obj.first.lower() in [ x.firstName.lower(), x.preferredName.lower(), x.nickName.lower() ] \
                and x.electionStatus == 'Running' ]

        if len(name_possibilities) == 1:
            cand = name_possibilities[0]
            if cand.electionStatus == 'Running':
                return cand.candidateId
            else:
                return None
        elif len(name_possibilities) > 1:
            self.too_many.append([(name_obj.first, name_obj.last)] + [ (x.firstName, x.lastName) for x in name_possibilities ])
        else:
            self.no_match.append([(name_obj.first, name_obj.last)] + [ (x.firstName, x.lastName) for x in name_possibilities ])



