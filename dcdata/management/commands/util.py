from django.db           import connections
from saucebrush.emitters import Emitter, DjangoModelEmitter
from saucebrush.filters  import Filter


class CountEmitter(Emitter):
    def __init__(self, every=1000, log=None, *args, **kwargs):
        super(CountEmitter, self).__init__(*args, **kwargs)
        self.count = 0
        self.every = every
        self.log = log

    def emit_record(self, record):
        if record:
            self.count += 1
            if self.count % self.every == 0:
                if self.log:
                    self.log.info("{0} records output...".format(self.count))
                else:
                    print self.count

    def done(self):
        if self.log:
            self.log.info("{0} total records output.".format(self.count))
        else:
            print "{0} total records output.".format(self.count)


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

    def __init__(self, inpath, log=None):
        self.inpath = inpath
        self.log = log

    def pre_drop(self):
        pass

    def post_create(self):
        pass

    def drop(self):
        self.pre_drop()
        if self.log:
            self.log.info("Dropping {0}.".format(self.db_table))
        else:
            print "Dropping {0}.".format(self.db_table)
        cursor = connections['default'].cursor()
        cursor.execute("drop table {0} cascade".format(self.db_table))


class SimpleDjangoModelEmitter(DjangoModelEmitter):
    """ Emitter that populates a table corresponding to a django model.

        Takes a Django model class and uses the ORM to insert the records into
        the appropriate table.
    """
    def __init__(self, model_class):
        # Don't want to do this, because of the crappy init:
        #   super(SimpleDjangoModelEmitter, self).__init__()
        #
        # Essentially need to do this...
        #   functools.partial(Emitter.__init__, self).__init__()
        #
        # ...but this will do the same, and it looks cleaner:
        Emitter.__init__(self)

        self._dbmodel = model_class



