from dcdata.loading              import Loader, LoaderEmitter
from dcdata.lobbying.models      import Lobbying, Lobbyist, Agency, Issue, Bill
from decimal                     import Decimal
from dcdata.management.base.importer import BaseImporter
from django.core                 import management
from django.db                   import connections
from saucebrush                  import run_recipe
from saucebrush.filters          import FieldModifier, UnicodeFilter, \
    Filter, FieldMerger
from saucebrush.sources          import CSVSource
from dcdata.management.commands.util import NoneFilter, CountEmitter, \
    TableHandler

import os, re


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

class LobbyingHandler(TableHandler):

    def __init__(self, inpath=None, log=None):
        super(LobbyingHandler, self).__init__(inpath)
        self.db_table = 'lobbying_lobbying'
        self.log = log

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
            CountEmitter(every=20000, log=self.log),
            LoaderEmitter(LobbyingLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            )),
        )


class AgencyHandler(TableHandler):

    def __init__(self, inpath=None, log=None):
        super(AgencyHandler, self).__init__(inpath)
        self.db_table = 'lobbying_agency'
        self.log = log

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldModifier('year', lambda x: int(x) if x else None),
            NoneFilter(),
            UnicodeFilter(),
            CountEmitter(every=10000, log=self.log),
            LoaderEmitter(AgencyLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )


class LobbyistHandler(TableHandler):

    def __init__(self, inpath=None, log=None):
        super(LobbyistHandler, self).__init__(inpath)
        self.db_table = 'lobbying_lobbyist'
        self.log = log

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldModifier('year', lambda x: int(x) if x else None),
            FieldModifier('member_of_congress', lambda x: x == 'True'),
            NoneFilter(),
            UnicodeFilter(),
            CountEmitter(every=20000, log=self.log),
            LoaderEmitter(LobbyistLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )


class IssueHandler(TableHandler):

    def __init__(self, inpath=None, log=None):
        super(IssueHandler, self).__init__(inpath)
        self.db_table = 'lobbying_issue'
        self.log = log

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldModifier('year', lambda x: int(x) if x else None),
            NoneFilter(),
            FieldModifier('specific_issue', lambda x: '' if x is None else x),
            UnicodeFilter(),
            CountEmitter(every=10000, log=self.log),
            LoaderEmitter(IssueLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )

class BillHandler(TableHandler):

    def __init__(self, inpath=None, log=None):
        super(BillHandler, self).__init__(inpath)
        self.db_table = 'lobbying_bill'
        self.log = log
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
            CountEmitter(every=20000, log=self.log),
            LoaderEmitter(BillLoader(
                source=self.inpath,
                description='load from denormalized CSVs',
                imported_by="loadlobbying (%s)" % os.getenv('LOGNAME', 'unknown'),
            ), commit_every=10000),
        )


HANDLERS = {
    "denorm_lob_lobbying": LobbyingHandler,
    "denorm_lob_lobbyist": LobbyistHandler,
    "denorm_lob_issue":    IssueHandler,
    "denorm_lob_agency":   AgencyHandler,
    "denorm_lob_bills":    BillHandler,
}

FILES = 'denorm_lob_lobbying.csv denorm_lob_lobbyist.csv denorm_lob_issue.csv denorm_lob_agency.csv denorm_lob_bills.csv'.split()

# main management command

class Command(BaseImporter):

    IN_DIR       = '/home/datacommons/data/auto/lobbying/denormalized/IN'
    DONE_DIR     = '/home/datacommons/data/auto/lobbying/denormalized/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/lobbying/denormalized/REJECTED'
    FILE_PATTERN = 'denorm_lob_*.csv'


    def do_first(self):
        for handler in HANDLERS.values():
            handler_obj = handler(None, self.log)
            handler_obj.drop()

        self.log.info("Syncing database to recreate dropped tables:")
        management.call_command('syncdb', interactive=False)

        for handler in HANDLERS.values():
            handler_obj = handler(None, self.log)
            handler_obj.post_create()

    def find_eligible_files(self):
        """
            Goes through the IN_DIR and finds files in the FILES array to work with
            We predefine the array so that the tables get loaded in the right order
        """

        present_files = [ os.path.join(self.IN_DIR, x) for x in FILES if x in os.listdir(self.IN_DIR) ]

        if len(present_files) > 0:
            for file_path in present_files:
                self.log.info('Found file {0}'.format(file_path))
                if self.file_has_not_been_written_to_for_over_a_minute(file_path):
                    yield file_path
                else:
                    self.log.info('File last modified time is too recent. Skipping.')
        else:
            self.log.info('No files found.')


    def do_for_file(self, file_path):
        handler_class = HANDLERS.get(os.path.basename(file_path).split('.')[0], None)

        if handler_class is None:
            self.log.fatal("!!! no handler for {0}".format(file_path))
        else:
            self.log.info("Found handler")
            handler = handler_class(file_path, self.log)
            self.log.info("Loading records for {0}".format(handler.db_table))
            handler.run()
            self.archive_file(file_path, True)

