from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.matching.models import HillStaffer
from dcentity.models import Entity

class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = HillStaffer.objects
        self.subject_id_type = 'integer'

        self.match = Entity.objects.extra(where=['id in (select entity_id from matchbox_entityattribute inner join lobbyist_ext_ids_2009_to_2011 on substring(lobbyist_ext_id for 11) = substring(value for 11))'])
        self.match_table_prefix = 'staffers'

        self.match_operator = 'istartswith'

