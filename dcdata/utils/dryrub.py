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
    
        
class FieldKeeper(Filter):
    """ Filter that keeps a given set of fields and removes all others.

        FieldKeeper(('spam', 'eggs')) removes all but the spam and eggs fields from
        every record filtered.
    """

    def __init__(self, keys):
        super(FieldKeeper, self).__init__()
        self._target_keys = utils.str_or_list(keys)

    def process_record(self, record):
        for key in record.keys():
           if not key in self._target_keys:
               record.pop(key, None)
        return record

class MD5Filter(Filter):
    
    def __init__(self, source_func, destination_field):
        self._source_func = source_func
        self._destination_field = destination_field
        
    def process_record(self, record):
        import hashlib
        value = self._source_func(record)
        if value:
            # hashlib wants an ascii string for some reason
            value = value.encode('ascii', 'replace')
            entity_id = hashlib.md5(value).hexdigest()
            record[self._destination_field] = entity_id
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


class NullEmitter(Emitter):
    """
        Does not emit record.
    """
    def emit_record(self, record):
        pass