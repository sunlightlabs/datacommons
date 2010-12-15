
from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, ComparisonField, FulltextField, \
    IndustryField
from dcapi.schema import Schema, FunctionField
from dcdata.contribution.models import Contribution
from dcdata.utils.sql import parse_date
from django.db.models.query_utils import Q
from urllib import unquote_plus


def _contributor_state_in_generator(query, *states):
    return query.filter(contributor_state__in=[state.upper() for state in states])
    

def _cycle_in_generator(query, *cycles):
    def dual_cycles(cycles):
        for cycle in cycles:
            yield int(cycle) - 1
            yield int(cycle)
    return query.filter(cycle__in=[cycle for cycle in dual_cycles(cycles)])
    
    
def _for_against_generator(query, for_against):
    if for_against == 'for':
        query = query.exclude(transaction_type__in=('24a','24n'))
    elif for_against == 'against':
        query = query.filter(transaction_type__in=('24a','24n'))
    return query


def _recipient_state_in_generator(query, *states):
    return query.filter(recipient_state__in=[state.upper() for state in states])


CONTRIBUTION_SCHEMA = Schema(
    FunctionField('contributor_state', _contributor_state_in_generator),
    FunctionField('recipient_state', _recipient_state_in_generator),
    FunctionField('cycle', _cycle_in_generator),
    FunctionField('for_against', _for_against_generator),
    IndustryField('contributor_industry', 'contributor_category'),
    InclusionField('seat'),
    InclusionField('transaction_namespace'),
    InclusionField('transaction_type'),
    InclusionField('contributor_ext_id'),
    InclusionField('recipient_ext_id'),
    InclusionField('organization_ext_id'),
    InclusionField('parent_organization_ext_id'),
    InclusionField('committee_ext_id'),
    ComparisonField('date', cast=parse_date),
    ComparisonField('amount', cast=int),
    FulltextField('committee_ft', ['committee_name']),                                                        
    FulltextField('contributor_ft', ['organization_name', 'parent_organization_name', 'contributor_employer', 'contributor_name']),
    FulltextField('employer_ft', ['organization_name', 'parent_organization_name', 'contributor_employer']), # deprecated!!!!                  
    FulltextField('organization_ft', ['organization_name', 'parent_organization_name', 'contributor_employer']),
    FulltextField('recipient_ft', ['recipient_name']),
)

def filter_contributions(request):    
    return CONTRIBUTION_SCHEMA.build_filter(Contribution.objects, request).order_by()


CONTRIBUTION_FIELDS = ['cycle', 'transaction_namespace', 'transaction_id', 'transaction_type', 'filing_id', 'is_amendment',
              'amount', 'date', 'contributor_name', 'contributor_ext_id', 'contributor_type', 'contributor_occupation',
              'contributor_employer', 'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state',
              'contributor_zipcode', 'contributor_category', 'contributor_category_order', 'organization_name',
              'organization_ext_id', 'parent_organization_name', 'parent_organization_ext_id', 'recipient_name',
              'recipient_ext_id', 'recipient_party', 'recipient_type', 'recipient_state', 'recipient_state_held',
              'recipient_category', 'recipient_category_order', 'committee_name', 'committee_ext_id', 'committee_party',
              'candidacy_status', 'district', 'district_held', 'seat', 'seat_held', 'seat_status',
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

