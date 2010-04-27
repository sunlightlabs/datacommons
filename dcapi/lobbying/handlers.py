
from urllib import unquote_plus
from django.db.models import Q
from piston.handler import BaseHandler
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
from dcdata.lobbying.models import Lobbying
from dcapi.lobbying import filter_lobbying

RESERVED_PARAMS = ('apikey','callback','limit','format','page','per_page','return_entities')
DEFAULT_PER_PAGE = 1000
MAX_PER_PAGE = 100000

LOBBYING_FIELDS = ['year', 'transaction_id', 'transaction_type', 'transaction_type_desc',
    'filing_type', 'amount', 'registrant_name', 'registrant_is_firm',
    'client_name', 'client_category', 'client_ext_id', 'client_parent_name',
    ('lobbyists', ('lobbyist_name','lobbyist_ext_id','candidate_ext_id','government_position','member_of_congress'))]

def load_lobbying(params, nolimit=False, ordering=True):
    
    per_page = min(int(params.get('per_page', DEFAULT_PER_PAGE)), MAX_PER_PAGE)
    page = int(params.get('page', 1)) - 1
    
    offset = page * per_page
    limit = offset + per_page
    
    for param in RESERVED_PARAMS:
        if param in params:
            del params[param]
            
    unquoted_params = dict([(param, unquote_plus(quoted_value)) for (param, quoted_value) in params.iteritems()])
    result = filter_lobbying(unquoted_params)
    if ordering:
        result = result.order_by('-year','-amount')
    if not nolimit:
        result = result[offset:limit]
          
    return result

class LobbyingStatsLogger(object):
    def __init__(self):
        self.stats = { 'total': 0 }
        self.stats[CRP_TRANSACTION_NAMESPACE] = 0
    def log(self, record):
        self.stats[CRP_TRANSACTION_NAMESPACE] += 1
        self.stats['total'] += 1

class LobbyingFilterHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = LOBBYING_FIELDS
    model = Lobbying
    statslogger = LobbyingStatsLogger
    
    def read(self, request):
        params = request.GET.copy()
        return load_lobbying(params)
