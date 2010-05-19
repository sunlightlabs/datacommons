from urllib import unquote_plus
from piston.handler import BaseHandler
from dcdata.grants.models import Grant
from dcapi.grants import filter_grants

RESERVED_PARAMS = ('apikey','callback','limit','format','page','per_page','return_entities')
DEFAULT_PER_PAGE = 1000
MAX_PER_PAGE = 100000

def load_grants(params, nolimit=False, ordering=True):
    
    per_page = min(int(params.get('per_page', DEFAULT_PER_PAGE)), MAX_PER_PAGE)
    page = int(params.get('page', 1)) - 1
    
    offset = page * per_page
    limit = offset + per_page
    
    for param in RESERVED_PARAMS:
        if param in params:
            del params[param]
            
    unquoted_params = dict([(param, unquote_plus(quoted_value)) for (param, quoted_value) in params.iteritems()])
    result = filter_grants(unquoted_params)
    if ordering:
        result = result.order_by('-fiscal_year','-amount_total')
    if not nolimit:
        result = result[offset:limit]
          
    return result

class GrantsFilterHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Grant
    
    def read(self, request):
        params = request.GET.copy()
        return load_grants(params)
