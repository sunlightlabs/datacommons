from dcdata.models import Import
from matchbox.models import Entity
from django.db.models import get_app, get_model, get_models
from saucebrush.emitters import Emitter
from saucebrush.filters import FieldFilter
import datetime

#
# saucebrush loading filters
#

class EntityFilter(FieldFilter):
    def process_field(self, item):
        if item and isinstance(item, basestring):
            return Entity.objects.get(pk=item)

class ISODateFilter(FieldFilter):
    def process_field(self, item):
        if item:
            (y, m, d) = item.split('-')
            return datetime.date(int(y), int(m), int(d))

class BooleanFilter(FieldFilter):
    def process_field(self, item):
        return item == 'True'

class FloatFilter(FieldFilter):
    def __init__(self, field, on_error=None):
        super(FloatFilter, self).__init__(field)
        self._on_error = on_error
    def process_field(self, item):
        try:
            return float(item)
        except ValueError:
            return self._on_error

class IntFilter(FieldFilter):
    def __init__(self, field, on_error=None):
        super(IntFilter, self).__init__(field)
        self._on_error = on_error
    def process_field(self, item):
        try:
            return int(item)
        except ValueError:
            return self._on_error

#
# utility method to get field names from Django models
#

def model_fields(label):
    (app_label, model_label) = label.split('.')
    app = get_app(app_label)
    model = get_model(app_label, model_label)
    model_fields = [field.name for field in model._meta.fields]
    return model_fields
    
#
# Loader class that will load a record into a Django model
#

class Loader(object):
    
    ID_FIELDS = ('id','uuid')
    
    model = None
    field_handlers = { }
    
    def __init__(self, source, description, imported_by):
        
        self.fields = { }
        for field in self.model._meta.fields:
            self.fields[field.name] = field
            
        self._new_record = dict([(f, None) for f in self.fields.iterkeys()])
        for key in self.ID_FIELDS:
            if key in self._new_record:
                del self._new_record[key]
        
        self.import_session = Import(
            source=source,
            description=description,
            imported_by=imported_by
        )
        self.import_session.save()
    
    def new_record(self):
        return self._new_record.copy()
        
    def load_records(self, records):
        for record in records:
            self.load_record(record)
    
    def load_record(self, record):
        
        if not self.model:
            raise ValueError, "model is required"
        
        obj = self._get_instance(record)
        
        for name, value in record.iteritems():
            
            if name in self.ID_FIELDS:
                raise ValueError, "not allowed to set ids during loading"
                
            field_handler = self.field_handlers.get(name, None)
            
            if field_handler:
                handler_value = field_handler(record, name, value, obj)
                if handler_value:
                    setattr(obj, name, handler_value)                    
            else:            
                field = self.fields.get(name, None)
                if field:
                    classname = field.__class__.__name__
                    if classname != 'ForeignKey':
                        setattr(obj, name, value)
    
        obj.import_reference = self.import_session
        obj.save()
    
    def _get_instance(self, record):
        raise NotImplementedError, "please inherit this class and override the _get_key method"


#
# saucebrush emitter
#

class LoaderEmitter(Emitter):
    def __init__(self, loader):
        super(LoaderEmitter, self).__init__()
        self._loader = loader
    def emit_record(self, record):
        self._loader.load_record(record)