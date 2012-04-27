from django.db.models import Q
from matching import MatchingCommand
from name_cleaver import PoliticianNameCleaver, RunningMatesNames

class PoliticianMatchingCommand(MatchingCommand):

    name_cleaver = PoliticianNameCleaver


    def cull_match_pool(self, subject_name, full_match_pool):
        matches_we_like = {}
        for match in full_match_pool:
            match_name = self.name_cleaver(getattr(match, self.match_name_attr)).parse()

            if isinstance(match_name, RunningMatesNames):
                for running_mate_name in match_name.mates():
                    confidence = self.get_confidence(running_mate_name, subject_name)
            else:
                confidence = self.get_confidence(match_name, subject_name)

            if confidence >= self.confidence_threshold:
                if not matches_we_like.has_key(confidence):
                    matches_we_like[confidence] = []

                matches_we_like[confidence].append(match)

        return matches_we_like


    def get_potential_matches_for_subject(self, subject_name, subject_obj):
        """
            Takes a name cleaver object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring
        """
        if not subject_obj.district:
            district_q = Q(politician_metadata_by_cycle__district_held__isnull=True) | Q(politician_metadata_by_cycle__district_held__in=['', '_'])
        else:
            district_str = '{0}-{1}'.format(subject_obj.state, subject_obj.padded_district)
            district_q = Q(politician_metadata_by_cycle__district_held=district_str)

        matches = self.match.filter(
            district_q,
            politician_metadata_by_cycle__cycle=subject_obj.cycle,
            politician_metadata_by_cycle__state_held=subject_obj.state,
            aliases__alias__icontains=subject_name.last,
        ).distinct()

        return matches
