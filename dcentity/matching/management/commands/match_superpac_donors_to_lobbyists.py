from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.matching.models import SuperPACDonor
from dcentity.models import Entity

class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = SuperPACDonor.objects
        self.subject_id_type = 'integer'

        self.match = Entity.objects.extra(where=['id in (select entity_id from matchbox_entityattribute inner join lobbyist_ext_ids_2008_to_2012 on lobbyist_ext_id = value)'])
        self.match_table_prefix = 'superpac'

        self.match_operator = 'istartswith'

