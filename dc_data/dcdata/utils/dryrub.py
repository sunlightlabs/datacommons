from saucebrush import utils
from saucebrush.filters import Filter, ConditionalFilter
from saucebrush.emitters import Emitter
#
# filters
#

class FieldCountValidator(ConditionalFilter):
    
    def __init__(self, field_count):
        super(FieldCountValidator, self).__init__()
        self.field_count = field_count
        
    def test_record(self, record):
        if len(record) != self.field_count:
            self.reject_record(record, "Expected %i columns, found %i" % (self.field_count, len(record)))
            return False
        return True
        
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

class EntityIDFilter(Filter):
    
    def __init__(self, field, key_template='%s'):
        self._field = field
        self._key_template = key_template
        
    def process_record(self, record):
        import hashlib, uuid
        value = record[self._field]
        if value:
            value = value.strip().decode('utf-8', 'ignore')
            entity_id = hashlib.md5(self._key_template % value).hexdigest()
            record['_id'] = entity_id
            record['suid'] = str(uuid.UUID(entity_id).int >> 64)
        return record
        

#
# emitters
#

class CountEmitter(Emitter):
    def __init__(self, every=1):
        import logging
        super(CountEmitter, self).__init__()
        self._every = every
        self._count = 0
    def emit_record(self, record):
        import logging
        self._count += 1
        if self._count % self._every == 0:
            logging.info('processed %i records' % self._count)


class NullEmitter(Emitter):
    """
        Does not emit record.
    """
    def emit_record(self, record):
        pass