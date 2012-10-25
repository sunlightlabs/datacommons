from dcdata.utils.log import set_up_logger
from dcentity.models import Entity
from django.conf import settings
from name_cleaver import PoliticianNameCleaver, IndividualNameCleaver, \
        OrganizationNameCleaver, PersonName

import re


class ReconcilerService(object):
    log = set_up_logger(
        'ReconcilerService',
        settings.LOGGING_DIRECTORY,
        'Unhappy Reconciler',
        email_recipients=settings.LOGGING_EMAIL['recipients']
    )

    def __init__(self, subject_name, entity_type, *args, **kwargs):
        self.subject_name = subject_name
        self.entity_type = entity_type

    def start(self, limit=None):
        if self.entity_type == 'politician':
            self.log.info("Trying name: {} with type: {} on PoliticianNameCleaver".format(self.subject_name, self.entity_type))
            subject_name_obj = self.try_name_cleaver_flavor(PoliticianNameCleaver)
            self.reconciler = PoliticianReconciler()

        elif self.entity_type == 'individual':
            self.log.info("Trying name: {} with type: {} on IndividualNameCleaver".format(self.subject_name, self.entity_type))
            subject_name_obj = self.try_name_cleaver_flavor(IndividualNameCleaver)
            self.reconciler = IndividualReconciler()
        else:
            self.log.info("Trying name: {} with type: {} on OrganizationNameCleaver".format(self.subject_name, self.entity_type))
            subject_name_obj = self.try_name_cleaver_flavor(OrganizationNameCleaver)
            self.reconciler = OrganizationReconciler()

        if not subject_name_obj:
            return []
        else:
            return self.reconciler.search(self, subject_name_obj)

    def try_name_cleaver_flavor(self, cleaver_class):
        try:
            subject_name = cleaver_class(self.subject_name).parse()

            # skip if we didn't get the right kind of result
            if cleaver_class.name_processing_failed(subject_name):
                self.log.debug('We didn\'t get a PoliticianName object back.')
                return
        except Exception, e:
            self.log.debug('Encountered an exception during name parsing.')
            self.log.debug(e)
            return

        return subject_name


class IndividualReconciler(object):
    name_cleaver = IndividualNameCleaver
    min_confidence_threshold = 1.2
    high_confidence_threshold = 3

    def __init__(self, *args, **kwargs):
        self.match = Entity.objects.filter(type='individual')
        self.match_name_attr = 'name'
        self.match_id_type = 'uuid'

        self.match_operator = 'icontains'

    def search(self, service, subject_name, limit=None):
        # search Match entities
        potential_matches = self.get_potential_matches_for_subject(subject_name)
        service.log.info('Potential matches: {0}; '.format(potential_matches.count()))

        matches_we_like = self.cull_match_pool(subject_name, potential_matches)

        return_vals = []
        confidence_levels = matches_we_like.keys()
        if len(confidence_levels):
            confidence_levels.sort()

            # this will insert all the matches at the highest confidence level
            confidence_cutoff = -2 if len(confidence_levels) > 1 else -1
            for confidence in confidence_levels[confidence_cutoff:]:
                for match in matches_we_like[confidence]:
                    return_vals.append(self.munge_match_into_result(match, confidence))

        return_vals.sort(key=lambda x: x['score'], reverse=True)

        return return_vals

    def munge_match_into_result(self, match, confidence):
        return {
            'id': match.pk,
            'name': match.name,
            'type': [match.type],
            'match': confidence >= self.high_confidence_threshold,
            'score': confidence,
        }

    def get_potential_matches_for_subject(self, subject_name):
        """
            Takes a name cleaver object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring.

            Note that while this base class method does not use subject_obj,
            child classes do use it to filter on metadata (e.g. state).
        """

        obj = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.last})

        return obj

    def cull_match_pool(self, subject_name, full_match_pool):
        matches_we_like = {}
        for match in full_match_pool:
            match_name = self.name_cleaver(match.name).parse()
            confidence = self.name_cleaver.compare(match_name, subject_name)

            if confidence >= self.min_confidence_threshold:
                #metadata_confidence = self.get_metadata_confidence(match, subject_obj)

                if confidence not in matches_we_like.keys():
                    matches_we_like[confidence] = []

                #matches_we_like[confidence].append((match,metadata_confidence))
                matches_we_like[confidence].append(match)

        return matches_we_like

class PoliticianReconciler(IndividualReconciler):
    name_cleaver = PoliticianNameCleaver
    min_confidence_threshold = 1.2
    high_confidence_threshold = 3

    def __init__(self, *args, **kwargs):
        self.match = Entity.objects.filter(type='politician')
        self.match_name_attr = 'name'
        self.match_id_type = 'uuid'

        self.match_operator = 'icontains'


class OrganizationReconciler(IndividualReconciler):
    name_cleaver = OrganizationNameCleaver
    min_confidence_threshold = 1
    high_confidence_threshold = 4

    def __init__(self, *args, **kwargs):
        self.match = Entity.objects.filter(type='organization')
        self.match_name_attr = 'name'
        self.match_id_type = 'uuid'

        self.match_operator = 'icontains'

    def get_potential_matches_for_subject(self, subject_name):
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
            matches = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, 'istartswith'): subject_name.crp_style_firm_name(False)})

        return matches




