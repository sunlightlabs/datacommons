from dcentity.matching.management.base.matching import MatchingCommand
from dcentity.models import Entity
from dcentity.matching.models import AlecSponsor



class Command(MatchingCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.subject = AlecSponsor.objects
        self.subject_name_attr = 'name'
        self.subject_id_type = 'integer'
        self.match = Entity.objects.filter(type='politician', attributes__namespace='urn:nimsp:recipient')
        self.match_table_prefix = 'alec'
        self.confidence_threshold = 1


    def get_potential_matches_for_subject(self, subject_name, subject_obj):
        match_set = self.match.filter(politician_metadata_by_cycle__state=subject_obj.state, politician_metadata_by_cycle__seat__icontains='state').distinct()

        return match_set.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.last})


    def get_confidence(self, name1, name2):
        score = 0
        if name1.last == name2.last:
            score += 1
        else:
            return 0

        if (name1.first and name2.first):
            if name1.first == name2.first:
                score += 1
            else:
                return 0

        return score


