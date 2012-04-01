from dcentity.matching.management.base.organizational_matching import OrganizationalMatchingCommand
from dcentity.matching.models import PublicCompany
from dcentity.models import Entity



class Command(OrganizationalMatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = PublicCompany.objects
        self.subject_name_attr = 'name'
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='organization')
        self.match_table_prefix = 'public_orgs_'



