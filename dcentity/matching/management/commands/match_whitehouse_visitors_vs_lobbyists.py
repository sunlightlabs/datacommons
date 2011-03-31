import re

from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.matching.models import WhiteHouseVisitor
from dcentity.models import Entity
from dcdata.lobbying.models import Lobbyist
from name_cleaver import SUFFIX_RE

class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = WhiteHouseVisitor.objects
        self.subject_id_type = 'integer'

        #self.match = Entity.objects.filter(attributes__value__in=['select lobbyist_ext_id from lobbyist_ext_ids_2009_to_2011'])
        self.match = Entity.objects.extra(where=['id in (select entity_id from matchbox_entityattribute inner join lobbyist_ext_ids_2009_to_2011 on lobbyist_ext_id = value)'])
        self.match_table_prefix = 'whitehouse'

        self.match_operator = 'istartswith'

        self.suffix_re = re.compile(SUFFIX_RE)

    def preprocess_subject_name(self, name):
        name = self.suffix_re.sub(' \1', name)
        name = re.sub(r'^DR(?=[BCDFGHJKLMNPQRSTVWXZ])$', 'DR ', name)

        return name
