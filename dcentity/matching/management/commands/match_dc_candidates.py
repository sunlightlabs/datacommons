from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.matching.models import DCCandidate, DCCandidateMetadataUnmatched

class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = DCCandidate.objects
        self.subject_id_type = 'integer'
        self.subject_name_attr = 'candidate'

        self.match = DCCandidateMetadataUnmatched.objects
        self.match_id_type = 'integer'
        self.match_name_attr = 'candidate_name'

        self.match_table_prefix = 'dc_meta'


