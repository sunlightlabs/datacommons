from dcdata.contracts.models import Contract
from dcdata.loading import Loader, LoaderEmitter
from django.core.management.base import CommandError, BaseCommand
from optparse import make_option
from saucebrush import run_recipe
from saucebrush.emitters import Emitter, DebugEmitter
from saucebrush.filters import FieldModifier, FieldRemover, UnicodeFilter
from saucebrush.sources import CSVSource
import os

class CountEmitter(Emitter):
    
    def __init__(self, every=1000):
        super(Emitter, self).__init__()
        self.every = every
        self.count = 0

    def emit_record(self, record):
        self.count += 1
        if self.count % self.every == 0:
            print "%s records" % self.count

class ContractLoader(Loader):
    model = Contract
    def __init__(self, *args, **kwargs):
        super(ContractLoader, self).__init__(*args, **kwargs)
    def get_instance(self, record):
        return self.model(id=record['id'])

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="file", help="path to input file", metavar="PATH"),
    )

    def handle(self, *args, **options):

        if 'file' not in options or options['file'] is None:
            raise CommandError("path to file is required")

        inpath = os.path.abspath(options['file'])
        
        run_recipe(
            CSVSource(open(inpath)),
            FieldRemover('import_reference'),
            UnicodeFilter(),
            FieldModifier('signed_date', lambda x: x if x else None),
            FieldModifier('effective_date', lambda x: x if x else None),
            FieldModifier('completion_date', lambda x: x if x else None),
            FieldModifier('maximum_date', lambda x: x if x else None),
            FieldModifier('renewal_date', lambda x: x if x else None),
            FieldModifier('cancellation_date', lambda x: x if x else None),
            #DebugEmitter(),
            CountEmitter(every=1000),
            LoaderEmitter(ContractLoader(
                source=inpath,
                description='load from denormalized CSVs',
                imported_by="loadcontracts (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )