from dcdata.guidestar.management.base.matching import MatchingCommand
from dcdata.guidestar.models import Officer
from dcentity.models import Entity

import re

class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = Officer
        self.match = Entity.objects.filter(type='politician')
        self.match_table_prefix = 'guidestar'

    def preprocess_subject_name(self, name):
        name = re.sub(r' CBO$', '', name)
        name = re.sub(r' PE C$', '', name)
        name = re.sub(r' M$', '', name)
        name = re.sub(r', M\.?D\.?$', '', name)

        return name


