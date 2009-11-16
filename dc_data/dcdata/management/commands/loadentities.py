from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from dcdata.loading import Loader, LoaderEmitter, IntFilter
from dcdata.utils.dryrub import CountEmitter
from matchbox.models import Entity
from saucebrush.emitters import DebugEmitter
from saucebrush.filters import Filter, FieldModifier, FieldRemover, UnicodeFilter
from saucebrush.sources import CSVSource
import saucebrush
import os

FIELDNAMES = ('count','name','urn','id')
TYPES = {
    'urn:crp:candidate': 'politician',
    'urn:crp:committee': 'committee',
    'urn:crp:organization': 'organization',
    'urn:crp:individual': 'individual',
}

class EntityLoader(Loader):
    
    model = Entity
    
    def __init__(self, *args, **kwargs):
        super(EntityLoader, self).__init__(*args, **kwargs)
        
    def get_instance(self, record):
        try:
            return Entity.objects.get(pk=record['id'])
        except Entity.DoesNotExist:
            return Entity()
    
    def resolve(self, record, obj):
        obj.count += record['count']


class TypeFilter(Filter):
    def process_record(self, record):
        if record['urn'] == '':
            record['type'] = 'organization'
        else:
            (namespace, identifier) = record['urn'].rsplit(':', 1)
            record['type'] = TYPES.get(namespace, None)
        return record


class Command(BaseCommand):

    help = "load entities from csv"
    args = ""

    requires_model_validation = False

    def handle(self, csvpath, *args, **options):

        loader = EntityLoader(
            source='entities',
            description='load from CSV',
            imported_by="loadentities.py (%s)" % os.getenv('LOGNAME', 'unknown'),
        )

        saucebrush.run_recipe(

            CSVSource(open(os.path.abspath(csvpath)), FIELDNAMES, skiprows=1),
            CountEmitter(every=100),

            FieldModifier('name', lambda s: s.strip()),
            IntFilter('count'),
            TypeFilter(),
            UnicodeFilter(),

            #DebugEmitter(),
            LoaderEmitter(loader),

        )
