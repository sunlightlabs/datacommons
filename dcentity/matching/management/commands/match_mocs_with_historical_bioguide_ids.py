from dcentity.matching.management.base.politician_matching import PoliticianMatchingCommand
from dcentity.matching.models import MemberOfCongressWithBioguide
from dcentity.models import Entity


class Command(PoliticianMatchingCommand):

    confidence_threshold = 1.1

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = MemberOfCongressWithBioguide.objects
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='politician', attributes__namespace='urn:crp:recipient')
        self.match_table_prefix = 'bioguide_historical'
        self.match_name_attr = 'name'


