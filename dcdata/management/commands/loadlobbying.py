from dcdata.loading              import Loader, LoaderEmitter
from dcdata.lobbying.models      import Lobbying, Lobbyist, Agency, Issue, Bill
from decimal                     import Decimal
from django.core.management.base import CommandError, BaseCommand
from django.core                 import management
from django.db                   import connections
from optparse                    import make_option
from saucebrush                  import run_recipe
from saucebrush.filters          import FieldModifier, UnicodeFilter, \
    Filter, FieldMerger
from saucebrush.sources          import CSVSource
from dcdata.management.commands.util import NoneFilter, CountEmitter, TableHandler

import os, re


class TransactionFilter(Filter):
    def __init__(self):
        self._cache = {}
    def process_record(self, record):
        transaction_id = record['transaction']
        transaction = self._cache.get(transaction_id, None)
        if transaction is None:
            try:
                #print "loading transaction %s from database" % transaction_id
                transaction = Lobbying.objects.get(pk=transaction_id)
                self._cache[transaction_id] = transaction
                #print "\t* loaded"
            except Lobbying.DoesNotExist:
                pass #print "\t* does not exist"
        if transaction:
            record['transaction'] = transaction
            return record

class IssueFilter(Filter):
    def __init__(self):
        self._cache = {}
    def process_record(self, record):
        issue_id = record['issue']
        issue = self._cache.get(issue_id, None)
        if issue is None:
            try:
                #print "loading issue %s from database" % issue_id
                issue = Issue.objects.get(pk=issue_id)
                self._cache[issue_id] = issue
                #print "\t* loaded"
            except Issue.DoesNotExist:
                pass #print "\t* does not exist"
        if issue:
            record['issue'] = issue
            return record
# loaders

class LobbyingLoader(Loader):
    model = Lobbying
    def __init__(self, *args, **kwargs):
        super(LobbyingLoader, self).__init__(*args, **kwargs)

    def get_instance(self, record):
        return self.model(transaction_id=record['transaction_id'])

class AgencyLoader(Loader):
    model = Agency
    def __init__(self, *args, **kwargs):
        super(AgencyLoader, self).__init__(*args, **kwargs)
    def get_instance(self, record):
        return self.model(transaction=record['transaction'], agency_ext_id=record['agency_ext_id'])

class IssueLoader(Loader):
    model = Issue
    def get_instance(self, record):
        return self.model(id=record['id'])

class BillLoader(Loader):
    model = Bill
    def __init__(self, *args, **kwargs):
        super(BillLoader, self).__init__(*args, **kwargs)
    def get_instance(self, record):
        return self.model(id=record['id'])

class LobbyistLoader(Loader):
    model = Lobbyist
    def __init__(self, *args, **kwargs):
        super(LobbyistLoader, self).__init__(*args, **kwargs)

    def get_instance(self, record):

        if record['transaction'] is None:
            return

        return self.model(transaction=record['transaction'], lobbyist_ext_id=record['lobbyist_ext_id'])

# handlers

TRANSACTION_FILTER = TransactionFilter()

class LobbyingHandler(TableHandler):

    def __init__(self, inpath):
        super(LobbyingHandler, self).__init__(inpath)
        self.db_table = 'lobbying_lobbying'

    def pre_drop(self):
        cursor = connections['default'].cursor()
        cursor.execute("drop view if exists lobbying_report")

    def post_create(self):
        cursor = connections['default'].cursor()
        cursor.execute("""
            create view lobbying_report as
                select *, case when year % 2 = 0 then year else year + 1 end as cycle
                from lobbying_lobbying l
                where use = 't'
        """, None)

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldModifier('year', lambda x: int(x) if x else None),
            FieldModifier('amount', lambda x: Decimal(x) if x else None),
            FieldModifier((
                'affiliate','filing_included_nsfs','include_in_industry_totals',
                'registrant_is_firm','use'), lambda x: x == 'True'),
            NoneFilter(),
            UnicodeFilter(),
            CountEmitter(every=1000),
            LoaderEmitter(LobbyingLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            )),
        )


class AgencyHandler(TableHandler):

    def __init__(self, inpath):
        super(AgencyHandler, self).__init__(inpath)
        self.db_table = 'lobbying_agency'

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldModifier('year', lambda x: int(x) if x else None),
            NoneFilter(),
            TRANSACTION_FILTER,
            UnicodeFilter(),
            CountEmitter(every=1000),
            LoaderEmitter(AgencyLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )


class LobbyistHandler(TableHandler):

    def __init__(self, inpath):
        super(LobbyistHandler, self).__init__(inpath)
        self.db_table = 'lobbying_lobbyist'

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldModifier('year', lambda x: int(x) if x else None),
            FieldModifier('member_of_congress', lambda x: x == 'True'),
            NoneFilter(),
            TRANSACTION_FILTER,
            UnicodeFilter(),
            CountEmitter(every=1000),
            LoaderEmitter(LobbyistLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )


class IssueHandler(TableHandler):

    def __init__(self, inpath):
        super(IssueHandler, self).__init__(inpath)
        self.db_table = 'lobbying_issue'

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldModifier('year', lambda x: int(x) if x else None),
            NoneFilter(),
            FieldModifier('specific_issue', lambda x: '' if x is None else x),
            TRANSACTION_FILTER,
            UnicodeFilter(),
            CountEmitter(every=1000),
            LoaderEmitter(IssueLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )

class BillHandler(TableHandler):

    def __init__(self, inpath):
        super(BillHandler, self).__init__(inpath)
        self.db_table = 'lobbying_bill'
        self.digits = re.compile(r'\D*(\d+)')
        # input values are the keys, target values to match opencongress bill types are the values
        self.bill_type_map = {
            'H':       'h',
            'HR':      'h',
            'HCON':    'hc',
            'HCONRES': 'hc',
            'HJ':      'hj',
            'HJRES':   'hj',
            'HRES':    'hr',
            'HRRES':   'hr',
            'S':       's',
            'SR':      's',
            'SCON':    'sc',
            'SCONRES': 'sc',
            'SJ':      'sj',
            'SJES':    'sj',
            'SJRES':   'sj',
            'SRES':    'sr',
        }


    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldMerger({'bill_type_raw': ['bill_name']}, lambda x: re.sub(r'[^A-Z]*', '', x), keep_fields=True),
            FieldMerger({'bill_type': ['bill_type_raw']}, lambda x: self.bill_type_map.get(x, None), keep_fields=True),
            FieldMerger({'bill_no': ['bill_name']}, lambda x: self.digits.match(x).groups()[0] if x and self.digits.match(x) else None, keep_fields=True),
            NoneFilter(),
            IssueFilter(),
            UnicodeFilter(),
            CountEmitter(every=1000),
            LoaderEmitter(BillLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )


HANDLERS = {
    "lob_lobbying": LobbyingHandler,
    "lob_lobbyist": LobbyistHandler,
    "lob_issue":    IssueHandler,
    "lob_agency":   AgencyHandler,
    "lob_bills":    BillHandler,
}

SOURCE_FILES = [ 'lob_lobbying', 'lob_lobbyist', 'lob_issue', 'lob_agency', 'lob_bills' ]

# main management command

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-d", "--dataroot", dest="dataroot", help="path to data directory", metavar="PATH"),
        make_option("-f", "--files", dest="files", help="source files", metavar="FILE[,FILE]"),
    )

    def handle(self, *args, **options):

        if 'dataroot' not in options or options['dataroot'] is None:
            raise CommandError("path to dataroot is required")

        dataroot = os.path.abspath(options['dataroot'])
        tables = options['files'].split(',') if options['files'] else SOURCE_FILES

        handlers = []

        tables.reverse() # this is so that we drop the tables in reverse (dependent-first) order
        for table in tables:
            print table
            inpath = os.path.join(dataroot, "denorm_%s.csv" % table)

            if os.path.exists(inpath):
                handler_class = HANDLERS.get(table, None)

                if handler_class is None:
                    raise Exception, "!!! no handler for %s" % table
                else:
                    print "found handler"
                    handler = handler_class(inpath)
                    handler.drop()
                    handlers.append(handler)

        print "Syncing database to recreate dropped tables:"
        management.call_command('syncdb', interactive=False)

        handlers.reverse() # this is to undo the last reverse and load the data in the intended (necessary) order
        for handler in handlers:
            handler.post_create()
            print "loading records for %s" % handler.db_table
            handler.run()

