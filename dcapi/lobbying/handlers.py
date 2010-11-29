from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema, FunctionField
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
from dcdata.lobbying.models import Lobbying


def _lobbyist_is_rep_generator(query, value):
    return query.filter(lobbyists__member_of_congress=True)


def _cat_order_generator(query, *orders):
    where_clause = 'client_category=catcode and catorder in (%s)' % ', '.join(["'%s'" % order.upper() for order in orders])
    return query.extra(tables=['agg_cat_map'], where=[where_clause])

def _cat_generator(query, *cats):
    return query.filter(client_category__in=[cat.upper() for cat in cats])

def _industry_generator(query, *industries):
    malformed_industries = [ind for ind in industries if len(ind) not in (3, 5)]
    if malformed_industries:
        raise ValueError("Arguments not valid industry categories or category orders: %s" % str(malformed_industries))
    
    orders = [order for order in industries if len(order)==3]
    if orders:
        query = _cat_order_generator(query, *orders)
        
    cats = [cat for cat in industries if len(cat)==5]
    if cats:
        query = _cat_generator(query, *cats)
        
    return query
    
    
LOBBYING_SCHEMA = Schema(
    FunctionField('lobbyist_is_rep', _lobbyist_is_rep_generator),
    FunctionField('industry', _industry_generator),

    InclusionField('transaction_id'),
    InclusionField('transaction_type'),
    InclusionField('filing_type'),
    InclusionField('year'),
    InclusionField('issue', 'issues__general_issue_code'),
    InclusionField('client_ext_id'),
    InclusionField('lobbyist_ext_id', 'lobbyists__lobbyist_ext_id'),
    InclusionField('candidate_ext_id', 'lobbyists__candidate_ext_id'),

    FulltextField('client_ft', ['client_name']),
    FulltextField('client_parent_ft', ['client_parent_name']),
    FulltextField('lobbyist_ft', ['lobbyist_name']),
    FulltextField('registrant_ft', ['registrant_name']),

    ComparisonField('amount', cast=int),
)

def filter_lobbying(request):
    q = LOBBYING_SCHEMA.build_filter(Lobbying.objects, request).order_by()
    # filter does nothing--it's here to force the join on lobbyists
    if 'lobbyist_ft' in request:
        q = q.filter(lobbyists__lobbyist_name__isnull=False)
    return q.select_related()


LOBBYING_FIELDS = ['year', 'transaction_id', 'transaction_type', 'transaction_type_desc',
    'filing_type', 'amount', 'registrant_name', 'registrant_is_firm',
    'client_name', 'client_category', 'client_ext_id', 'client_parent_name',
    ('lobbyists', ('lobbyist_name','lobbyist_ext_id','candidate_ext_id','government_position','member_of_congress')),
    ('issues', ('general_issue_code','general_issue','specific_issue')),
    ('agencies', ('agency_ext_id','agency_name')),]


class LobbyingStatsLogger(object):
    def __init__(self):
        self.stats = { 'total': 0 }
        self.stats[CRP_TRANSACTION_NAMESPACE] = 0
    def log(self, record):
        self.stats[CRP_TRANSACTION_NAMESPACE] += 1
        self.stats['total'] += 1


class LobbyingFilterHandler(FilterHandler):
    fields = LOBBYING_FIELDS
    model = Lobbying
    statslogger = LobbyingStatsLogger
    ordering = ['-year','-amount']
    filename = 'lobbying'
    
    def queryset(self, params):
        return filter_lobbying(self._unquote(params))
    
    