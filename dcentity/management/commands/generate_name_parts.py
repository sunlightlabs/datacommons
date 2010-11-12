from django.core.management.base import BaseCommand
from dcentity.models             import Entity, EntityAlias, EntityNameParts
from name_cleaver.name_cleaver   import PoliticianNameCleaver
import sys

DEBUG = False

class Command(BaseCommand):
    args = ''
    help = 'Breaks up CRP politician names into their respective parts'

    def handle(self, *args, **options):
        for alias in EntityAlias.objects.filter(entity__type='politician', entity__attributes__namespace='urn:crp:recipient'):
            name_obj = PoliticianNameCleaver(alias.alias).parse()
            if name_obj.suffix and len(name_obj.suffix) > 3:
                print name_obj
                print name_obj.suffix
            name_parts = EntityNameParts.objects.get_or_create(
                alias  = alias,
                first  = name_obj.first,
                middle = name_obj.middle,
                last   = name_obj.last,
                suffix = name_obj.suffix,
            )
            sys.stdout.write('.')


