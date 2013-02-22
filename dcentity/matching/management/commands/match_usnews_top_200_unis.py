from dcentity.matching.management.base.organizational_matching import OrganizationalMatchingCommand
from dcentity.matching.models import USNewsTop200University
from dcentity.models import Entity
import re



class Command(OrganizationalMatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = USNewsTop200University.objects
        self.subject_name_attr = 'name'
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='organization')
        self.match_table_prefix = 'top_200_unis'


    def preprocess_subject_name(self, name):
        return re.sub('--.*$', '', name)

