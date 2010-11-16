
from dcapi.common.handlers import FilterHandler
from dcapi.contributions import filter_contributions
from dcdata.contribution.models import Contribution
from urllib import unquote_plus


CONTRIBUTION_FIELDS = ['cycle', 'transaction_namespace', 'transaction_id', 'transaction_type', 'filing_id', 'is_amendment',
              'amount', 'date', 'contributor_name', 'contributor_ext_id', 'contributor_type', 'contributor_occupation', 
              'contributor_employer', 'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state',
              'contributor_zipcode', 'contributor_category', 'contributor_category_order', 'organization_name', 
              'organization_ext_id', 'parent_organization_name', 'parent_organization_ext_id', 'recipient_name',
              'recipient_ext_id', 'recipient_party', 'recipient_type', 'recipient_state', 'recipient_category', 'recipient_category_order',
              'committee_name', 'committee_ext_id', 'committee_party', 'election_type', 'district', 'seat', 'seat_status',
              'seat_result']


class ContributionStatsLogger(object):
    def __init__(self):
        self.stats = { 'total': 0 }
    def log(self, record):
        if isinstance(record, dict):
            ns = record.get('transaction_namespace', 'unknown')
        else:
            ns = getattr(record, 'transaction_namespace', 'unknown')
        self.stats[ns] = self.stats.get(ns, 0) + 1
        self.stats['total'] += 1


class ContributionFilterHandler(FilterHandler):
    fields = CONTRIBUTION_FIELDS
    model = Contribution
    statslogger = ContributionStatsLogger
    ordering = ['-cycle','-amount']
    filename = 'contributions'
    
    def queryset(self, params):
        return filter_contributions(self._unquote(params))
