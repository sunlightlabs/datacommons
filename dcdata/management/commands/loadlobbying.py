from dcdata.loading import Loader, LoaderEmitter
from dcdata.lobbying.models import Lobbying, Lobbyist, Agency, Issue
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
        if record:
            self.count += 1
            if self.count % self.every == 0:
                print self.count

class NoneFilter(Filter):
    def process_record(self, record):
        for key, value in record.iteritems():
            if isinstance(value, basestring) and value.strip() == '':
                record[key] = None
        return record

class YearFilter(Filter):
    def __init__(self, year, field='year'):
        self.year = year
        self.field = field
    def process_record(self, record):
        if self.year and self.year == record[self.field]:
            return record

class TransactionFilter(Filter):
    def __init__(self):
        self._cache = {}
    def process_record(self, record):
        transaction_id = record['transaction']
        transaction = self._cache.get(transaction_id, None)
        if transaction is None:
            try:
                transaction = Lobbying.objects.get(pk=transaction_id)
                self._cache[transaction_id] = transaction
            except Lobbying.DoesNotExist:
                pass # transaction is still None
        record['transaction'] = transaction
        return record

# loaders

class LobbyingLoader(Loader):
    model = Lobbying
    def __init__(self, *args, **kwargs):
        super(LobbyingLoader, self).__init__(*args, **kwargs)
        
    def get_instance(self, record):
        #try:
        #    return self.model.objects.get(transaction_id=record['transaction_id'])
        #except Lobbying.DoesNotExist:
            return self.model(transaction_id=record['transaction_id'])

class IssueLoader(Loader):
    model = Issue
    def __init__(self, *args, **kwargs):
        super(IssueLoader, self).__init__(*args, **kwargs)
    def get_instance(self, record):
        #try:
        #    return self.model.objects.get(id=record['id'])
        #except self.model.DoesNotExist:
            return self.model(id=record['id'])

class LobbyistLoader(Loader):
    model = Lobbyist
    def __init__(self, *args, **kwargs):
        super(LobbyistLoader, self).__init__(*args, **kwargs)
        
    def get_instance(self, record):
        
        if record['transaction'] is None:
            return
        
        #try:
        #    return self.model.objects.get(transaction=record['transaction'], lobbyist_ext_id=record['lobbyist_ext_id'])
        #except Lobbyist.DoesNotExist:
        return self.model(transaction=record['transaction'], lobbyist_ext_id=record['lobbyist_ext_id'])

# handlers

transaction_filter = TransactionFilter()

def lobbying_handler(inpath, year=None):
    run_recipe(
        CSVSource(open(inpath)),
        YearFilter(year),
        FieldModifier('year', lambda x: int(x) if x else None),
        FieldModifier('amount', lambda x: Decimal(x) if x else None),
        FieldModifier((
            'affiliate','filing_included_nsfs','include_in_industry_totals',
            'registrant_is_firm','use'), lambda x: x == 'True'),
        NoneFilter(),
        UnicodeFilter(),
        #DebugEmitter(),
        CountEmitter(every=100),
        LoaderEmitter(LobbyingLoader(
            source=inpath,
            description='load from denormalized CSVs',
            imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
        )),
    )

def lobbyist_handler(inpath, year=None):
    run_recipe(
        CSVSource(open(inpath)),
        YearFilter(year),
        FieldModifier('year', lambda x: int(x) if x else None),
        FieldModifier('member_of_congress', lambda x: x == 'True'),
        NoneFilter(),
        transaction_filter,
        UnicodeFilter(),
        #DebugEmitter(),
        CountEmitter(every=100),
        LoaderEmitter(LobbyistLoader(
            source=inpath,
            description='load from denormalized CSVs',
            imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
        ), commit_every=10000),
    )

def issue_handler(inpath, year=None):
    run_recipe(
        CSVSource(open(inpath)),
        YearFilter(year),
        FieldModifier('year', lambda x: int(x) if x else None),
        NoneFilter(),
        transaction_filter,
        UnicodeFilter(),
        #DebugEmitter(),
        CountEmitter(every=100),
        LoaderEmitter(IssueLoader(
            source=inpath,
            description='load from denormalized CSVs',
            imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
        ), commit_every=10000),
    )
    

HANDLERS = {
    "lob_lobbying": lobbying_handler,
    "lob_lobbyist": lobbyist_handler,
    "lob_issue": issue_handler,
}

#TABLES = ('lob_lobbying','lob_lobbyist')
#TABLES = ('lob_lobbying',)
TABLES = ('lob_lobbyist','lob_issue')

# main management command

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-d", "--dataroot", dest="dataroot", help="path to data directory", metavar="PATH"),
        make_option("-y", "--year", dest="year", help="year to load", metavar="YEAR"),
    )

    def handle(self, *args, **options):

        if 'dataroot' not in options or options['dataroot'] is None:
            raise CommandError("path to dataroot is required")

        dataroot = os.path.abspath(options['dataroot'])
        year = options.get('year', None)

        for table in TABLES:
            
            infields = FILE_TYPES[table]
            inpath = os.path.join(dataroot, "denorm_%s.csv" % table)

            if os.path.exists(inpath):
                handler = HANDLERS.get(table, None)
                
                if handler is None:
                    print "!!! no handler for %s" % table
                else:
                    print "loading records for %s" % table
                    handler(inpath, year)