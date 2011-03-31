from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.matching.models import Officer
from dcentity.models import Entity

import re

class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = Officer.objects
        self.match = Entity.objects.filter(type='politician')
        self.match_table_prefix = 'matching'

    def preprocess_subject_name(self, name):
        name = re.sub(r' CBO$', '', name)
        name = re.sub(r' PE C$', '', name)
        name = re.sub(r' M$', '', name)
        name = re.sub(r', M\.?D\.?$', '', name)

        return name


