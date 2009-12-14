from saucebrush.emitters import CSVEmitter, DebugEmitter

class EntityEmitter(CSVEmitter):
    
    fields = ('id','name','type','timestamp','reviewer')
    
    def __init__(self, csvfile, timestamp):
        super(EntityEmitter, self).__init__(csvfile, self.fields)
        self._timestamp = timestamp
        
    def emit_record(self, record):
        super(EntityEmitter, self).emit_record(dict(zip(self.fields, (
            record['id'],
            record['name'],
            'organization',
            self._timestamp,
            'basic entity script - jcarbaugh',
        ))))

class EntityAttributeEmitter(CSVEmitter):
    
    fields = ('entity','namespace','value')
    
    def __init__(self, csvfile):
        super(EntityAttributeEmitter, self).__init__(csvfile, self.fields)
        
    def emit_record(self, record):
        super(EntityAttributeEmitter, self).emit_record(dict(zip(self.fields, (
            record['id'],
            'urn:matchbox:entity',
            record['id'],
        ))))


class EntityAliasEmitter(CSVEmitter):
    
    fields = ('entity','alias')
    
    def __init__(self, csvfile):
        super(EntityAliasEmitter, self).__init__(csvfile, self.fields)
        
    def emit_record(self, record):
        super(EntityAliasEmitter, self).emit_record(dict(zip(self.fields, (
            record['id'],
            record['name'],
        ))))