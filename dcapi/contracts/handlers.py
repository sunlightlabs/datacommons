from urllib import unquote_plus
from piston.handler import BaseHandler
from dcdata.contracts.models import Contract
from dcapi.contracts import filter_contracts

RESERVED_PARAMS = ('apikey','callback','limit','format','page','per_page','return_entities')
DEFAULT_PER_PAGE = 1000
MAX_PER_PAGE = 100000

def load_contracts(params, nolimit=False, ordering=True):
    
    per_page = min(int(params.get('per_page', DEFAULT_PER_PAGE)), MAX_PER_PAGE)
    page = int(params.get('page', 1)) - 1
    
    offset = page * per_page
    limit = offset + per_page
    
    for param in RESERVED_PARAMS:
        if param in params:
            del params[param]
            
    unquoted_params = dict([(param, unquote_plus(quoted_value)) for (param, quoted_value) in params.iteritems()])
    result = filter_contracts(unquoted_params)
    if ordering:
        result = result.order_by('-fiscal_year','-current_amount')
    if not nolimit:
        result = result[offset:limit]
          
    return result

class ContractsFilterHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Contract
    
    def read(self, request):
        params = request.GET.copy()
        return load_contracts(params)
