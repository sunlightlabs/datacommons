from django.core.management.base import BaseCommand
from dcdata.earmarks.models      import Member
from dcentity.models             import Entity
from name_cleaver.name_cleaver   import PoliticianNameCleaver
from itertools                   import groupby

chamber_map = {
    's': 'federal:senate',
    'h': 'federal:house',
}

DEBUG = True

class Command(BaseCommand):
    args = ''
    help = 'Matches member names with existing CRP IDs and entity names'

    def handle(self, *args, **options):
        self.successes = 0
        self.failures_no_match = 0
        self.failures_too_many = 0

        for member in Member.objects.filter(crp_id='').values('raw_name', 'chamber', 'state').distinct():
            name_obj = PoliticianNameCleaver(member['raw_name']).parse()

            state_possibilities = self.get_set_of_states_from_earmark(member)

            kwargs = self.build_query_kwargs(member, chamber_map, name_obj)

            entities = self.entity_query_set(name_obj, kwargs)

            if (not member.get('state')) or entities.count() == 0: # state might be wrong, so try the whole list of states

                if kwargs.has_key('politician_metadata__state'):
                    kwargs.pop('politician_metadata__state')

                kwargs['politician_metadata__state__in'] = state_possibilities
                entities = self.entity_query_set(name_obj, kwargs)

            # main decision block
            if len(entities) == 0:
                self.failures_no_match += 1

                if DEBUG:
                    self.print_member(member, state_possibilities)
                    print "- No match!"

            elif len(entities) > 1:
                if DEBUG:
                    self.prompt_on_too_many_matches(member, state_possibilities, entities)
                else:
                    self.failures_too_many += 1

            elif len(entities) == 1:
                self.update_member(member, entities[0])
                self.successes += 1


    def report_results(self):
        print "Successes: {0}".format(self.successes)
        print "No match: {0}".format(self.failures_no_match)
        print "Too many: {0}".format(self.failures_too_many)


    def get_set_of_states_from_earmark(self, member):
        state_possibilities = []
        for member_line_item in Member.objects.filter(raw_name=member['raw_name'], chamber=member['chamber']):
            states = member_line_item.earmark.house_states if member_line_item.chamber == 'h' else member_line_item.earmark.senate_states
            state_possibilities.extend([x.strip() for x in states.split(';') if len(x.strip()) == 2])

        state_possibilities.sort()
        return [ key for key,_ in groupby(state_possibilities) ] # unique


    def build_query_kwargs(self, member, chamber_map, name_obj):
        kwargs = {}
        self.add_to_query_if_not_null(kwargs, 'politician_metadata__state', member.get('state'))
        self.add_to_query_if_not_null(kwargs, 'politician_metadata__party', member.get('party'))
        self.add_to_query_if_not_null(kwargs, 'politician_metadata__seat', chamber_map.get(member['chamber']))
        self.add_to_query_if_not_null(kwargs, 'aliases__name_parts__first', name_obj.first)
        return kwargs


    def entity_query_set(self, name_obj, kwargs):
        return Entity.objects \
            .filter(
                type='politician',
                aliases__name_parts__last=name_obj.last,
                bioguide_info__bioguide_id__isnull=False,
                **kwargs
            ) \
            .extra(where=['matchbox_entity.id in (select entity_id from agg_entities where cycle >= 2006 and agg_entities.entity_id = matchbox_entity.id)']) \
            .distinct()


    def prompt_on_too_many_matches(self, member, state_possibilities, entities):
        self.print_member(member, state_possibilities)
        count = 1

        for entity in entities:
            meta = entity.politician_metadata
            print "{0}: {1}|{2}|{3}|{4}".format(count, entity.name, meta.state, meta.party, meta.seat)
            count += 1

        choice = raw_input("Too many matches. Choose an entity if possible, or enter S to skip: ")

        choice = choice.strip()

        if choice not in ['S', 's']:
            self.update_member(member, entities[int(choice)-1])
            self.successes += 1
        else:
            self.failures_too_many += 1


    def print_member(self, member, state_possibilities=[]):
        print "{0}|{1}|{2}|{3}|{4}".format(member.get('raw_name'), member.get('chamber'), member.get('party'), member.get('state'), state_possibilities)


    def add_to_query_if_not_null(self, kwargs, criterion, value):
        if value:
            kwargs[criterion] = value


    def update_member(self, member, entity):
        member_objs = Member.objects.filter(
            raw_name=member.get('raw_name'),
            chamber=member.get('chamber'),
            state=member.get('state'),
        ).update(
            crp_id=entity.attributes.get(namespace='urn:crp:recipient').value,
            standardized_name=entity.name,
        )
        self.print_member(member)
        print '- Updated for state {0}!'.format(entity.politician_metadata.state)


