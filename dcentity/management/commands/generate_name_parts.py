from django.core.management.base import BaseCommand
from dcentity.models             import EntityAlias, EntityNameParts
from name_cleaver.name_cleaver   import PoliticianNameCleaver
import sys

DEBUG = False

class Command(BaseCommand):
    args = ''
    help = 'Breaks up CRP politician names into their respective parts'

    def handle(self, *args, **options):
        aliases = EntityAlias.objects.filter(
            entity__type='politician',
            entity__attributes__namespace='urn:crp:recipient',
        ).exclude(
            name_parts__isnull=False
        )

        print aliases.query
        print '----------------------------------------------\n\n'

        for alias in aliases:
            if DEBUG:
                print alias.alias
                print alias.id

            name_obj = PoliticianNameCleaver(alias.alias).parse()

            if DEBUG:
                print str(name_obj)
                print '--------------------'

            name_parts = EntityNameParts.objects.get_or_create(
                alias  = alias,
                first  = name_obj.first,
                middle = name_obj.middle,
                last   = name_obj.last,
                suffix = name_obj.suffix,
            )

            if not DEBUG:
                sys.stdout.write('.')


