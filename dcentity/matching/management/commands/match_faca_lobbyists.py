from dcentity.matching.management.base.matching import MatchingCommand
from dcdata.faca.models import FACANormalizedMember
from dcentity.models import Entity

class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = FACANormalizedMember.objects
        self.subject_id_type = 'integer'
        self.subject_name_attr = 'name'

        self.match = Entity.objects.extra(where=['id in (select entity_id from matchbox_entityattribute inner join assoc_lobbying_lobbyist using (entity_id))'])
        self.match_table_prefix = 'faca_lob'

        self.match_operator = 'istartswith'


