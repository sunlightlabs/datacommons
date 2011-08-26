from dcentity.matching.management.base.organizational_matching import OrganizationalMatchingCommand
from dcentity.models import Entity
from dcentity.matching.models import HonorariumRegistrant



class Command(OrganizationalMatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = HonorariumRegistrant.objects
        self.subject_name_attr = 'name'
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='organization')
        self.match_table_prefix = 'ks'

