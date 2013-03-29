from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, ComparisonField, FulltextField
from dcapi.schema import Schema, FunctionField
from dcdata.contribution.models import ContributionDC
from dcdata.utils.sql import parse_date

def _contributor_state_in_generator(query, *states):
    return query.filter(contributor_state__in=[state.upper() for state in states])


#def _cycle_in_generator(query, *cycles):
#    def dual_cycles(cycles):
#        for cycle in cycles:
#            yield int(cycle) - 1
#            yield int(cycle)
#    return query.filter(cycle__in=[cycle for cycle in dual_cycles(cycles)])


def _recipient_state_in_generator(query, *states):
    return query.filter(recipient_state__in=[state.upper() for state in states])


CONTRIBUTION_SCHEMA = Schema(
    FulltextField('committee_ft', ['committee_name']),                                                        
    FulltextField('contributor_ft', ['contributor_name']),
    FunctionField('contributor_state', _contributor_state_in_generator),
    InclusionField('contributor_type'),
    InclusionField('contributor_zipcode'),
    InclusionField('contributor_zipcode'),
    ComparisonField('amount', cast=int),
    ComparisonField('date', cast=parse_date),
    #FunctionField('cycle', _cycle_in_generator),
    #InclusionField('seat'),
    #InclusionField('transaction_namespace'),
    #InclusionField('committee_ext_id'),
    #FulltextField('recipient_ft', ['recipient_name']),
)

def filter_contributions(request):
    query = CONTRIBUTION_SCHEMA.build_filter(ContributionDC.objects, request).order_by()
    print query.query
    return query


CONTRIBUTION_FIELDS = [
    'transaction_id', 'committee_name', 'contributor_name', 'contributor_entity', 'contributor_type', 
    'contributor_type_internal', 'payment_type', 'contributor_address', 'contributor_city', 'contributor_state',
    'contributor_zipcode', 'amount', 'date'
    ]


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



class ContributionDCFilterHandler(FilterHandler):
    fields = CONTRIBUTION_FIELDS
    model = ContributionDC
    statslogger = ContributionStatsLogger
    ordering = ['-amount']
    filename = 'contributions_dc'
    
    def queryset(self, params):
        return filter_contributions(self._unquote(params))


