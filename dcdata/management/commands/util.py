from django.db           import connections
from saucebrush.emitters import Emitter
from saucebrush.filters  import Filter


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


class TableHandler(object):
    """
        Base table handler which takes care of deleting old records
        Must be run in conjunction with a call to syncdb
    """
    db_table = None
    inpath = None

    def __init__(self, inpath):
        self.inpath = inpath

    def pre_drop(self):
        pass

    def post_create(self):
        pass

    def drop(self):
        self.pre_drop()
        print "Dropping {0}.".format(self.db_table)
        cursor = connections['default'].cursor()
        cursor.execute("drop table {0} cascade".format(self.db_table))

