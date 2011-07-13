from django.core.management.base import BaseCommand
from django.db.models            import Q
from dcdata.earmarks.models      import Recipient
from dcentity.models             import Entity
import difflib, re

DEBUG = True
STOP_WORDS = ['INC', 'CORPORATION', 'INCORPORATED', 'CORP', 'LLC', 'AND', '&', 'THE']

class Command(BaseCommand):
    args = ''
    help = 'Matches recipient names with existing organization entity names'

    successes_count = 0
    failures_too_many_count = 0
    failures_no_match_count = 0

    failures_too_many = []
    failures_no_match = []


    def handle(self, *args, **options):
        for earmark in Recipient.objects.filter(standardized_recipient='').exclude(raw_recipient='').values('raw_recipient').distinct():
            raw_name = earmark['raw_recipient']
            name = earmark['raw_recipient']
            name = name.split(',')[0]
            name = name.strip()
            name = re.sub(r'\s+\(.*\)\s*$', '', name)
            tokens = name.split(' ')
            tokens = [ x for x in tokens if x.upper() not in STOP_WORDS ]

            startswith = (Q(name__istartswith=tokens[0]) | Q(name__istartswith=tokens[1])) \
                if re.search('\bthe\b', tokens[0]) \
                else Q(name__istartswith=tokens[0])

            entities = Entity.objects \
                .filter(type='organization') \
                .extra(where=["to_tsvector('datacommons', name) @@ to_tsquery('datacommons', quote_literal(%s))"], params=[' '.join(tokens)]) \
                .exclude(name__icontains='party') \
                .exclude(name__icontains='democrat') \
                .exclude(name__icontains='republican') \
                .filter(startswith)

            if len(entities) > 0:
                ranked_matches = self.rank_matches(name, entities)
                print u'{0}:'.format(name.lower())

                if len(ranked_matches) == 1:
                    winning_entity = Entity.objects.get(name__iexact=ranked_matches[0])
                    Recipient.objects.filter(raw_recipient=raw_name).update(standardized_recipient=winning_entity.name)
                    print '- Updated!'
                    self.successes_count += 1

                elif len(ranked_matches) > 1:
                    if DEBUG:
                        self.prompt_on_too_many_matches(name, raw_name, entities)
                else:
                    if DEBUG:
                        self.prompt_on_too_many_matches(name, raw_name, entities)

                self.failures_too_many_count += 1
                self.failures_too_many.append(name)
            else:
                self.failures_no_match_count += 1
                self.failures_no_match.append(name)

        print "Successes: {0}".format(self.successes_count)
        print "--------------------------------------------------------------------------------------------------------------"
        print "Too many matches: {0}".format(self.failures_too_many_count)
        print self.failures_too_many
        print "--------------------------------------------------------------------------------------------------------------"
        print "No matches: {0}".format(self.failures_no_match_count)
        print self.failures_no_match


    def update_from_ranked(self, raw, standard):
        Earmark.objects.filter(raw_recipient=raw).update(standardized_recipient=standard)
        print u'{0}:'.format(raw)
        print '- Updated!'

    def rank_matches(self, name, entities):
        n = 2

        if len(name) < 4:
            cutoff = 1
        elif len(name) < 6:
            cutoff = 0.8
        else:
            cutoff = 0.75

        if name:
            entity_names = [ x.name.lower() for x in entities if \
                    len(x.name.split(' ')) - len(name.split(' ')) < 2 \
                    and ( \
                        name.lower().startswith(x.name.split(' ')[0].lower()) \
                        or re.sub('(?i)^the ', '', name).lower().startswith(x.name.split(' ')[0].lower()) \
                    ) \
            ]

            return difflib.get_close_matches(name.lower(), entity_names)

    def prompt_on_too_many_matches(self, name, raw_name, entities=None, ranked_matches=None):
        count = 1

        if entities:
            for entity in entities:
                print "{0}: {1}".format(count, entity.name)
                count += 1
        else:
            for match in ranked_matches:
                print "{0}: {1}".format(count, match)
                count += 1

        choice = raw_input("Too many matches. Choose an entity if possible, or enter S to skip: [1]")

        choice = choice.strip() if choice.strip() != '' else 1

        if choice not in ['S', 's']:
            if entities:
                Recipient.objects.filter(raw_recipient=raw_name).update(standardized_recipient=entities[int(choice)-1].name)
            else:
                winning_entity = Entity.objects.get(name__iexact=ranked_matches[0])
                Recipient.objects.filter(raw_recipient=raw_name).update(standardized_recipient=winning_entity.name)

            self.successes_count += 1
        else:
            self.failures_too_many_count += 1


