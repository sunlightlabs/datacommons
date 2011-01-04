from dcdata.loading              import Loader, LoaderEmitter
from dcdata.lobbying.models      import Lobbying, Lobbyist, Agency, Issue
from dcdata.lobbying.sources.crp import FILE_TYPES
from decimal                     import Decimal
from django.core.management.base import CommandError, BaseCommand
from django.core                 import management
from django.db                   import connections
from optparse                    import make_option
from saucebrush                  import run_recipe
from saucebrush.emitters         import DebugEmitter, Emitter
from saucebrush.filters          import FieldModifier, UnicodeFilter, Filter
from saucebrush.sources          import CSVSource

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
    def done(self):
        print "%s total records" % self.count

class NoneFilter(Filter):
    def process_record(self, record):
        for key, value in record.iteritems():
            if isinstance(value, basestring) and value.strip() == '':
                record[key] = None
        return record

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

class LobbyistLoader(Loader):
    model = Lobbyist
    def __init__(self, *args, **kwargs):
        super(LobbyistLoader, self).__init__(*args, **kwargs)

    def get_instance(self, record):

        if record['transaction'] is None:
            return

        return self.model(transaction=record['transaction'], lobbyist_ext_id=record['lobbyist_ext_id'])

# handlers

transaction_filter = TransactionFilter()

class TableHandler(object):
    db_table = None
    inpath = None

    def __init__(self, inpath):
        self.inpath = inpath

    def drop(self):
        print "Dropping {0}.".format(self.db_table)
        cursor = connections['default'].cursor()
        cursor.execute("drop table {0}".format(self.db_table))


class LobbyingHandler(TableHandler):

    def __init__(self, inpath):
        super(LobbyingHandler, self).__init__(inpath)
        self.db_table = 'lobbying_lobbying'

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
            #DebugEmitter(),
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
            transaction_filter,
            UnicodeFilter(),
            #DebugEmitter(),
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
            transaction_filter,
            UnicodeFilter(),
            #DebugEmitter(),
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
            transaction_filter,
            UnicodeFilter(),
            #DebugEmitter(),
            CountEmitter(every=1000),
            LoaderEmitter(IssueLoader(
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
}

SOURCE_FILES = [ 'lob_lobbying','lob_lobbyist','lob_issue','lob_agency' ]

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
            infields = FILE_TYPES[table]
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
            print "loading records for %s" % table
            handler.run()

