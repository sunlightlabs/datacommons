from urllib import unquote_plus
from piston.handler import BaseHandler
from django.core.paginator import Paginator

RESERVED_PARAMS = ('apikey','callback','limit','format','page','per_page','return_entities')
DEFAULT_PER_PAGE = 1000
MAX_PER_PAGE = 1000000


class FilterHandler(BaseHandler):
    
    # To be overriden by subclasses
    
    # must have either a model or fields (or both)
    model = None 
    fields = None   
    ordering = []
    filename = 'download'
        
    def queryset(self, params):
        raise NotImplementedError
    
            
    # Base class functionality
    
    def __init__(self):
        """ If fields not present, then fill in based on model. """
        
        if not self.fields:
            self.fields = self.model._meta.get_all_field_names()
            if 'id' in self.fields:
                self.fields.remove('id')
            if 'import_reference' in self.fields:
                self.fields.remove('import_reference')
    
    allowed_methods = ('GET',)
    
    def _unquote(self, params):
        return dict([(param, unquote_plus(quoted_value)) for (param, quoted_value) in params.iteritems()])
    
    def read(self, request):
        params = request.GET.copy()

        print params['per_page']
        per_page = int(params.get('per_page', DEFAULT_PER_PAGE))
        print per_page
        per_page = min(per_page, MAX_PER_PAGE)
        print per_page

        page = int(params.get('page', 1))
        
        for param in RESERVED_PARAMS:
            if param in params:
                del params[param]
                        
        qs = self.queryset(params).order_by(*self.ordering)
        print per_page
        pg = Paginator(qs.all(), per_page)
        return pg.page(page)


class DenormalizingFilterHandler(FilterHandler):
    simple_fields = []
    relation_fields = []
    
    def __init__(self):
        self.fields = self.simple_fields + self.relation_fields
    
    def _denormalize(self, data):
        result = dict((field, getattr(data, field)) for field in self.simple_fields)
        
        for relation in self.relation_fields:
            result[relation] = "; ".join(str(o) for o in getattr(data, relation).all())
        
        return result

    def read(self, request):
        for earmark in super(DenormalizingFilterHandler, self).read(request):
            yield self._denormalize(earmark)
