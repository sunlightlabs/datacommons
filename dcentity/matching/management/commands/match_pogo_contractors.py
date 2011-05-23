from dcentity.matching.management.base.matching import MatchingCommand
from dcdata.pogo.models import Contractor
from dcentity.models import Entity
from name_cleaver import OrganizationNameCleaver, OrganizationName

#import re


class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = Contractor.objects
        self.subject_name_attr = 'name'
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='organization')
        self.match_table_prefix = 'matching_pogo'

        self.name_cleaver = OrganizationNameCleaver

    def preprocess_subject_name(self, name):
        return name


    def get_potential_matches_for_subject(self, subject):
        """
            Takes a name cleaver-ed object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring
        """
        # if we don't get a wide range of matches from the kernel of the name here...
        # which would be the case for names like "Massachusetts Inst. of Technology"
        # which will fail the "icontains" operator when the kernel is 'Massachusetts Technology'
        matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject.kernel()})
        # try the normal name
        if not matches.count():
            matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject.name})
        # and if that doesn't work, try the expanded name 'Massachusetts Institute of Technology'
        if not matches.count():
            matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject.expand()})

        return matches


    def name_processing_failed(self, subject_name):
        return not isinstance(subject_name, OrganizationName)


    def get_confidence(self, name1, name2):
        """
            Accepts two name objects from name cleaver
        """
        if name1.expand().lower() == name2.expand().lower():
            return 4
        elif name1.kernel().lower() == name2.kernel().lower():
            return 3
        else:
            return 2



