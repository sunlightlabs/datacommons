import sys
from saucebrush import utils
from saucebrush.filters import Filter, ConditionalFilter
from saucebrush.emitters import Emitter
from dcdata.processor import SkipRecordException
from saucebrush.sources import CSVSource
#
# filters
#

class FieldCountValidator(Filter):
    
    def __init__(self, field_count):
        super(FieldCountValidator, self).__init__()
        self.field_count = field_count
        
    def process_record(self, record):
        if len(record) == self.field_count:
            return record
        else:
            raise SkipRecordException('Expected %d fields, found %d.' % (self.field_count, len(record)))
        
        
class VerifiedCSVSource(CSVSource):
    EXTRA_FIELDS = object()
    MISSING_VALUE = object()
    
    def __init__(self, csvfile, fieldnames=None, skiprows=0, **kwargs):
        super(VerifiedCSVSource, self).__init__(csvfile, fieldnames, skiprows, 
                                                restkey=VerifiedCSVSource.EXTRA_FIELDS, 
                                                restval=VerifiedCSVSource.MISSING_VALUE,
                                                **kwargs)

class CSVFieldVerifier(Filter):
    def __init__(self):
        super(CSVFieldVerifier, self).__init__()
        
    def process_record(self, record):
        if VerifiedCSVSource.EXTRA_FIELDS in record:
            raise SkipRecordException('Extra fields found in record: %s' % record[VerifiedCSVSource.EXTRA_FIELDS])
        if VerifiedCSVSource.MISSING_VALUE in record.values():
            raise SkipRecordException('Missing fields found in record: %s' % ([key for (key, value) in record.items() if value == VerifiedCSVSource.MISSING_VALUE]))

        return record
    
        
#
# emitters
#

class CountEmitter(Emitter):
    def __init__(self, every=1, file=sys.stdout):
        super(CountEmitter, self).__init__()
        self._every = every
        self._count = 0
        self._file = file
    def emit_record(self, record):
        self._count += 1
        if self._count % self._every == 0:
            self._file.write('processed %i records\n' % self._count)
            self._file.flush()

