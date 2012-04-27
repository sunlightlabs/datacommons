from dcentity.matching.management.base.matching import MatchingCommand
from dcdata.contribution.models import LobbyistBundle
from dcentity.models import Entity
from django.db.models import F

class Command(MatchingCommand):


    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = LobbyistBundle.objects.exclude(name=F('employer'))
        self.subject_name_attr = 'name'
        self.subject_id_type = 'integer'

        self.match = Entity.objects.filter(type='individual').extra(where=['id in (select entity_id from assoc_lobbying_lobbyist)'])
        self.match_table_prefix = 'bundler_indiv'

