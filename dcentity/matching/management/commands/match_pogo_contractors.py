from dcentity.matching.management.base.matching import OrganizationalMatchingCommand
from dcdata.pogo.models import Contractor
from dcentity.models import Entity



class Command(OrganizationalMatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = Contractor.objects
        self.subject_name_attr = 'name'
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='organization')
        self.match_table_prefix = 'matching_pogo'


    def do_after_insert(self, subject, match, confidence):
        attribute = match.attributes.objects.get_or_create(namespace='urn:pogo:contractor')
        attribute.value = subject.id
        attribute.save()


