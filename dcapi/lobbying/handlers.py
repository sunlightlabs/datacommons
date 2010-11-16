from dcapi.common.handlers import FilterHandler
from dcapi.lobbying import filter_lobbying
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
from dcdata.lobbying.models import Lobbying


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