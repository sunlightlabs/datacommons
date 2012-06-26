from dcentity.matching.management.base.organizational_matching import OrganizationalMatchingCommand
from dcdata.contribution.models import LobbyistBundle
from dcentity.models import Entity

class Command(OrganizationalMatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = LobbyistBundle.objects.filter(employer__isnull=False) \
                .extra(where=['employer not in (select name from assoc_bundler_matches_manual)']).order_by('employer')
        self.subject_name_attr = 'employer'
        self.subject_id_type = 'integer'

        self.match = Entity.objects.filter(type='organization').extra(where=[
            'id in (select entity_id from assoc_lobbying_registrant)',
        ])
        self.match_table_prefix = 'bundler_employer'


