from dcdata.models import Import
from dcdata.processor import TerminateProcessingException, SkipRecordException
from django.db import transaction
from django.db.models import get_model
from saucebrush.emitters import Emitter
from saucebrush.filters import FieldFilter
import sys

#
# saucebrush loading filters
#

class BooleanFilter(FieldFilter):
    def process_field(self, item):
        return item == 'True'

#
# utility method to get field names from Django models
#

def model_fields(label):
    (app_label, model_label) = label.split('.')
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
    
    def __init__(self, source, description, imported_by, **kwargs):

        self.log = kwargs['log']
        
        # populate a fieldname/field mapping of model fields
        self.fields = { }
        for field in self.model._meta.fields:
            self.fields[field.name] = field
        
        # create a record template with field names from model
        # remove any fields that are typical ID fields
        self._new_record = dict([(f, None) for f in self.fields.iterkeys()])
        for key in self.ID_FIELDS:
            if key in self._new_record:
                del self._new_record[key]
        
        # create a new Import instance and save reference
        self.import_session = Import(
            source=source,
            description=description,
            imported_by=imported_by
        )
        self.import_session.save()
    
    def new_record(self):
        """ Get an empty copy of record format.
        """
        return self._new_record.copy() # return record template
        
    def load_records(self, records):
        """ Load a list of records.
        """
        for record in records:
            self.load_record(record)
    
    def load_record(self, record):
        """ Load a dict record into a model and save
            to the database.
        """
        
        # a model is required for loading
        if not self.model:
            raise ValueError, "model is required"
        
        # get a new or existing instance of model
        obj = self.get_instance(record)
        
        if obj is None:
            return
        
        if obj.pk:
            # object already exists, resolve issue of "conflicting" data
            self.resolve(record, obj)
        else:
            # object is new, copy over all fields
            self.copy_fields(record, obj)
    
        # assign Import reference and save
        obj.import_reference = self.import_session
        
        try:
            obj.save()
        except ValueError:
            self.log.warn(record)
            self.log.warn('Error saving record to database: %s -- %s' % (sys.exc_info()[0], sys.exc_info()[1]), sys.exc_info()[2])
            raise SkipRecordException('Error saving record to database: %s -- %s' % (sys.exc_info()[0], sys.exc_info()[1]), sys.exc_info()[2])            
        except:
            print record
            print 'Fatal error saving record to database: %s -- %s' % (sys.exc_info()[0], sys.exc_info()[1]), sys.exc_info()[2]
            raise TerminateProcessingException('Fatal error saving record to database: %s -- %s' % (sys.exc_info()[0], sys.exc_info()[1]), sys.exc_info()[2])
    
    def copy_fields(self, record, obj):    
        """ Copy fields from a record to an instance of a model.
        """
        
        # iterate over record key/values
        for name, value in record.iteritems():
        
            # raise an error if ID is being set
            # if name in self.ID_FIELDS:
            #     raise ValueError, "not allowed to set ids during loading"
            
            # see if a handler exists for the field
            field_handler = self.field_handlers.get(name, None)
        
            if field_handler:
                # call field handler and set on instance
                handler_value = field_handler(record, name, value, obj)
                if handler_value:
                    setattr(obj, name, handler_value)                    
            else:
                # no handler so just set the value on the object if the field exists
                field = self.fields.get(name, None)
                if field:
                    #classname = field.__class__.__name__
                    #if classname != 'ForeignKey':
                    setattr(obj, name, value)
    
    def get_instance(self, record):
        raise NotImplementedError, "please inherit this class and override the get_instance method"
    
    def resolve(self, record, obj):
        # copy fields, override if you want specific update actions
        self.copy_fields(record, obj)


#
# saucebrush emitter
#

# to do: no need for this class to exist
class LoaderEmitter(Emitter):
    def __init__(self, loader, commit_every=0):
        super(LoaderEmitter, self).__init__()
        self._loader = loader
        self._commit_every = 0
        self._count = 0
    def process_record(self, record):
        self.emit_record(record)
        return record
    def emit_record(self, record):
        self._loader.load_record(record)
        self._count += 1
        if self._commit_every and self._count % self._commit_every == 0:
            transaction.commit()
            
