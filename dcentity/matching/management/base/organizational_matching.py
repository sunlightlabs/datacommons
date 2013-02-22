from dcentity.matching.management.base.matching import MatchingCommand
from name_cleaver.names                         import OrganizationName
from name_cleaver.cleaver                       import OrganizationNameCleaver
import re

class OrganizationalMatchingCommand(MatchingCommand):
    name_cleaver = OrganizationNameCleaver

    def __init__(self, *args, **kwargs):
        super(OrganizationalMatchingCommand, self).__init__(*args, **kwargs)


    def name_processing_failed(self, subject_name):
        return not isinstance(subject_name, OrganizationName)


    def get_potential_matches_for_subject(self, subject_name, subject_obj):
        """
            Takes a name cleaver-ed object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring
        """
        # if we don't get a wide range of matches from the kernel of the name here...
        # which would be the case for names like "Massachusetts Inst. of Technology"
        # which will fail the "icontains" operator when the kernel is 'Massachusetts Technology'
        matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.kernel()})
        # try the normal name
        if not matches.count():
            matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.name})
        # and if that doesn't work, try the expanded name 'Massachusetts Institute of Technology'
        if not matches.count():
            matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.expand()})
        # and if that doesn't work, try a wildcard search
        if not matches.count():
            matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, 'iregex'): re.sub(' ', '.*', subject_name.kernel())})
        # and if that doesn't work, try the CRP-style firm name
        if not matches.count():
            matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, 'istartswith'): self.crp_style_firm_name(subject_name, False)})

        return matches


    def get_confidence(self, match, subject):
        """
            Accepts two name objects from name cleaver
        """
        if match.expand().lower() == subject.expand().lower():
            return 4
        elif match.kernel().lower() == subject.kernel().lower():
            return 3
        # law and lobbying firms in CRP data typically list only the first two partners
        # before 'et al'
        elif ',' in subject.expand(): # we may have a list of partners
            if self.crp_style_firm_name(subject) == str(match).lower():
                return 3
        else:
            return 2

    def crp_style_firm_name(self, name_obj, with_et_al=True):
        if with_et_al:
            return ', '.join(name_obj.kernel().split()[0:2] + ['et al'])
        else:
            return ', '.join(name_obj.kernel().split()[0:2])




