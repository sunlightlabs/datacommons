from dcdata.loading import Loader, LoaderEmitter
from dcdata.lobbying.models import Lobbying, Lobbyist, Agency
from dcdata.lobbying.sources.crp import FILE_TYPES, MODELS
from decimal import Decimal
from django.core.management.base import CommandError, BaseCommand
from optparse import make_option
from saucebrush import run_recipe
from saucebrush.emitters import DebugEmitter, Emitter
from saucebrush.filters import FieldModifier, UnicodeFilter, Filter
from saucebrush.sources import CSVSource
import os

# util emitters and filters

class CountEmitter(Emitter):
    def __init__(self, every=1000, *args, **kwargs):
        super(CountEmitter, self).__init__(*args, **kwargs)
        self.count = 0
        self.every = every
    def emit_record(self, record):
        self.count += 1
        if self.count % self.every == 0:
            print self.count

class NoneFilter(Filter):
    def process_record(self, record):
        for key, value in record.iteritems():
            if isinstance(value, basestring) and value.strip() == '':
                record[key] = None
        return record

# loaders

class LobbyingLoader(Loader):
    model = Lobbying
    def __init__(self, *args, **kwargs):
        super(LobbyingLoader, self).__init__(*args, **kwargs)
        
    def get_instance(self, record):
        try:
            return self.model.objects.get(transaction_id=record['transaction_id'])
        except Lobbying.DoesNotExist:
            return self.model(transaction_id=record['transaction_id'])

class LobbyistLoader(Loader):
    model = Lobbyist
    def __init__(self, *args, **kwargs):
        super(LobbyistLoader, self).__init__(*args, **kwargs)
        
    def get_instance(self, record):
        try:
            return self.model.objects.get(transaction=Lobbying.objects.get(pk=record['transaction_id']), lobbyist_ext_id=record['lobbyist_ext_id'])
        except Lobbyist.DoesNotExist:
            return self.model(transaction__pk=record['transaction_id'], lobbyist_ext_id=record['lobbyist_ext_id'])

# handlers

def lobbying_handler(inpath):
    run_recipe(
        CSVSource(open(inpath)),
        FieldModifier('year', lambda x: int(x) if x else None),
        FieldModifier('amount', lambda x: Decimal(x) if x else None),
        FieldModifier((
            'affiliate','filing_included_nsfs','include_in_industry_totals',
            'registrant_is_firm','use'), lambda x: x == 'True'),
        NoneFilter(),
        UnicodeFilter(),
        DebugEmitter(),
        CountEmitter(every=5000),
        LoaderEmitter(LobbyingLoader(
            source=inpath,
            description='load from denormalized CSVs',
            imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
        )),
    )

def lobbyist_handler(inpath):
    run_recipe(
        CSVSource(open(inpath)),
        FieldModifier('year', lambda x: int(x) if x else None),
        FieldModifier('member_of_congress', lambda x: x == 'True'),
        NoneFilter(),
        UnicodeFilter(),
        #DebugEmitter(),
        CountEmitter(every=5000),
        LoaderEmitter(LobbyistLoader(
            source=inpath,
            description='load from denormalized CSVs',
            imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
        )),
    )

HANDLERS = {
    "lob_lobbying": lobbying_handler,
    "lob_lobbyist": lobbyist_handler,
}

TABLES = ('lob_lobbying','lob_lobbyist')

# main management command

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-d", "--dataroot", dest="dataroot", help="path to data directory", metavar="PATH"),)

    def handle(self, *args, **options):

        if 'dataroot' not in options or options['dataroot'] is None:
            raise CommandError("path to dataroot is required")

        dataroot = os.path.abspath(options['dataroot'])

        for table in TABLES:
            
            infields = FILE_TYPES[table]
            inpath = os.path.join(dataroot, "denorm_%s.csv" % table)

            if os.path.exists(inpath):
                handler = HANDLERS.get(table, None)
                
                if handler is None:
                    print "!!! no handler for %s" % table
                else:
                    print "loading records for %s" % table
                    handler(inpath)