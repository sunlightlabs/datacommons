from dcdata.utils.log import set_up_logger
from dcentity.models import Entity
from django.conf import settings
from django.db.models import Q
from name_cleaver import PoliticianNameCleaver, IndividualNameCleaver, \
        OrganizationNameCleaver
from name_cleaver.exception import UnparseableNameException

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
        self.subject_properties = kwargs.get('properties')

    def start(self, limit=None):
        if self.entity_type == 'politician':
            self.log.info(u"Trying name: {} with type: {} on PoliticianNameCleaver".format(self.subject_name, self.entity_type))
            subject_name_obj = self.try_name_cleaver_flavor(PoliticianNameCleaver)
            self.reconciler = PoliticianReconciler()

        elif self.entity_type == 'individual':
            self.log.info(u"Trying name: {} with type: {} on IndividualNameCleaver".format(self.subject_name, self.entity_type))
            subject_name_obj = self.try_name_cleaver_flavor(IndividualNameCleaver)
            self.reconciler = IndividualReconciler()
        else:
            self.log.info(u"Trying name: {} with type: {} on OrganizationNameCleaver".format(self.subject_name, self.entity_type))
            subject_name_obj = self.try_name_cleaver_flavor(OrganizationNameCleaver)
            self.reconciler = OrganizationReconciler()

        if not subject_name_obj:
            return []
        else:
            return self.reconciler.search(self, subject_name_obj, subject_properties=self.subject_properties)

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

    def search(self, service, subject_name, limit=None, subject_properties=None):
        # search Match entities
        potential_matches = self.get_potential_matches_for_subject(subject_name, subject_properties=subject_properties)
        service.log.info(u'Potential matches: {0}; '.format(potential_matches.count()))

        matches_we_like = self.cull_match_pool(subject_name, potential_matches, service)
        service.log.info(u'Culled matches: {}'.format(len(matches_we_like)))

        return_vals = []
        confidence_levels = matches_we_like.keys()
        if len(confidence_levels):
            confidence_levels.sort()

            # this will insert all the matches at the highest confidence level
            confidence_cutoff = -2 if len(confidence_levels) > 1 else -1
            for confidence in confidence_levels[confidence_cutoff:]:
                for match, match_name in matches_we_like[confidence]:
                    return_vals.append(self.munge_match_into_result(match, match_name, confidence))

        return_vals.sort(key=lambda x: x['score'], reverse=True)

        return return_vals

    def munge_match_into_result(self, match, match_name, confidence):
        return {
            'id': match.pk,
            'name': match_name,
            'type': [match.type],
            'match': confidence >= self.high_confidence_threshold,
            'score': confidence,
        }

    def get_potential_matches_for_subject(self, subject_name, subject_properties=None):
        """
            Takes a name cleaver object and ideally returns a loosely matched set of objects
            which we can then filter more stringently by scoring.

            Note that while this base class method does not use subject_obj,
            child classes do use it to filter on metadata (e.g. state).
        """

        obj = self.match.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.last})

        return obj

    def cull_match_pool(self, subject_name, full_match_pool, service):
        matches_we_like = {}
        for match in full_match_pool:
            try:
                match_name = self.name_cleaver(match.name).parse()
            except UnparseableNameException as e:
                service.log.debug(u"Couldn't parse name {} for match entity id {}".format(match.name, match.id))

            if self.name_cleaver.name_processing_failed(match_name):
                continue
            else:
                confidence = self.name_cleaver.compare(match_name, subject_name)
                service.log.debug(u"Match {}: {} found to have confidence {}".format(match.id, match.name, confidence))

                if confidence >= self.min_confidence_threshold:
                    #metadata_confidence = self.get_metadata_confidence(match, subject_obj)

                    if confidence not in matches_we_like.keys():
                        matches_we_like[confidence] = []

                    #matches_we_like[confidence].append((match,metadata_confidence))
                    matches_we_like[confidence].append((match, str(match_name)))

        return matches_we_like


class PoliticianReconciler(IndividualReconciler):
    name_cleaver = PoliticianNameCleaver
    min_confidence_threshold = 1
    high_confidence_threshold = 2

    def __init__(self, *args, **kwargs):
        self.match = Entity.objects.filter(type='politician')
        self.match_name_attr = 'name'
        self.match_id_type = 'uuid'

        self.match_operator = 'icontains'

    def get_potential_matches_for_subject(self, subject_name, subject_properties=None):
        if subject_properties:
            office_map = {
                'US House': 'federal:house',
                'US Senate': 'federal:senate',
                'President': 'federal:president',
            }

            skip_state = None
            skip_district = None

            match_set = self.match

            if subject_properties.get('office'):
                office = office_map[subject_properties['office']]
                match_set = match_set.filter(politician_metadata_by_cycle__seat=office)

            #    if office is 'federal:president':
            #        skip_state = True
            #        skip_district = True
            #    elif office is 'federal:senate':
            #        skip_district = True

            #if not skip_state and subject_properties.get('state'):
            #    match_set = match_set.filter(politician_metadata_by_cycle__state=subject_properties.get('state'))

            #if not skip_district and subject_properties.get('district'):
            #    match_set = match_set.filter(politician_metadata_by_cycle__district__contains=subject_properties.get('district'))

            match_set = match_set.filter(politician_metadata_by_cycle__cycle__gte=2010).distinct()

            return match_set.filter(**{'{0}__{1}'.format(self.match_name_attr, self.match_operator): subject_name.last})
        else:
            return super(PoliticianReconciler, self).get_potential_matches_for_subject(subject_name)


class OrganizationReconciler(IndividualReconciler):
    name_cleaver = OrganizationNameCleaver
    min_confidence_threshold = 1
    high_confidence_threshold = 4

    def __init__(self, *args, **kwargs):
        self.match = Entity.objects.filter(type='organization')
        self.match_name_attr = 'name'
        self.match_id_type = 'uuid'

        self.match_operator = 'icontains'

    def get_potential_matches_for_subject(self, subject_name, subject_properties=None):
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




