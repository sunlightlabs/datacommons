from urllib import unquote_plus
from piston.handler import BaseHandler

RESERVED_PARAMS = ('apikey','callback','limit','format','page','per_page','return_entities')
DEFAULT_PER_PAGE = 1000
MAX_PER_PAGE = 100000


class FilterHandler(BaseHandler):
    
    # To be overriden by subclasses
    model = None    
    ordering = []
        
    def queryset(self, params):
        raise NotImplementedError
    
            
    # Base class functionality
    
    allowed_methods = ('GET',)
    
    def _unquote(self, params):
        return dict([(param, unquote_plus(quoted_value)) for (param, quoted_value) in params.iteritems()])
    
    def read(self, request):
        params = request.GET.copy()

        per_page = min(int(params.get('per_page', DEFAULT_PER_PAGE)), MAX_PER_PAGE)
        page = int(params.get('page', 1)) - 1
        
        offset = page * per_page
        limit = offset + per_page
        
        for param in RESERVED_PARAMS:
            if param in params:
                del params[param]
                        
        return self.queryset(params).order_by(*self.ordering)[offset:limit]

