from django.db.models import Q

from dcapi.aggregates.handlers import execute_top
from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, ComparisonField, FulltextField, \
    IndustryField, query_to_ft_sql, _fulltext_clause
from dcapi.schema import Schema, FunctionField, Field
from dcdata.contribution.models import Contribution
from dcdata.utils.sql import parse_date
from dcapi.contributions.transaction_types import add_transaction_type_description


class MSAField(Field):
    
    def __init__(self, name):
        super(MSAField, self).__init__(name)

    def apply(self, query, msa_name):
        return query.extra(tables=['geo_msa', 'geo_zip'],
                    where=["contribution_contribution.contributor_zipcode = geo_zip.zipcode",
                           "geo_zip.msa_id = geo_msa.id",
                           _fulltext_clause('geo_msa.name')],
                    params=[query_to_ft_sql(msa_name)])


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
        query = query.exclude(transaction_type__in=('24a','24n', '29'))
    elif for_against == 'against':
        query = query.filter(transaction_type__in=('24a','24n'))
    elif for_against == 'electioneering':
        query = query.filter(transaction_type='29')
    return query


def _recipient_state_in_generator(query, *states):
    return query.filter(recipient_state__in=[state.upper() for state in states])


def _general_transaction_type_generator(query, *general_types):
    if 'all' in general_types:
        return query

    def _generator(general_type):        
        if general_type == 'standard':
            return Q(transaction_type__in=('', '10', '11', '15', '15e', '15j', '22y', '24k', '24r', '24z'))
        if general_type == 'ie_supporting':
            return Q(transaction_type='24e')
        if general_type == 'ie_opposing':
            return Q(transaction_type='24a')
        if general_type == 'electioneering':
            return Q(transaction_type='29')
    
    return query.filter(reduce(lambda x, y: x | y, [_generator(general_type) for general_type in general_types]))


CONTRIBUTION_SCHEMA = Schema(
    FunctionField('contributor_state', _contributor_state_in_generator),
    FunctionField('recipient_state', _recipient_state_in_generator),
    FunctionField('cycle', _cycle_in_generator),
    FunctionField('for_against', _for_against_generator),
    FunctionField('general_transaction_type', _general_transaction_type_generator),
    IndustryField('contributor_industry', 'contributor_category'),
    InclusionField('seat'),
    InclusionField('transaction_namespace'),
    InclusionField('transaction_type'),
    InclusionField('contributor_ext_id'),
    InclusionField('recipient_ext_id'),
    InclusionField('organization_ext_id'),
    InclusionField('parent_organization_ext_id'),
    InclusionField('committee_ext_id'),
    InclusionField('contributor_type'),
    InclusionField('recipient_type'),
    ComparisonField('date', cast=parse_date),
    ComparisonField('amount', cast=int),
    FulltextField('committee_ft', ['committee_name']),                                                        
    FulltextField('contributor_ft', ['organization_name', 'parent_organization_name', 'contributor_employer', 'contributor_name']),
    FulltextField('employer_ft', ['organization_name', 'parent_organization_name', 'contributor_employer']), # deprecated!!!!                  
    FulltextField('organization_ft', ['organization_name', 'parent_organization_name', 'contributor_employer']),
    FulltextField('recipient_ft', ['recipient_name']),
    MSAField('msa_ft')
)

def filter_contributions(request):    
    return CONTRIBUTION_SCHEMA.build_filter(Contribution.objects, request).order_by()


CONTRIBUTION_FIELDS = ['cycle', 'transaction_namespace', 'transaction_id', 'transaction_type', 'transaction_type_description', 'filing_id', 'is_amendment',
              'amount', 'date', 'contributor_name', 'contributor_ext_id', 'contributor_type', 'contributor_occupation',
              'contributor_employer', 'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state',
              'contributor_zipcode', 'contributor_category', 'organization_name',
              'organization_ext_id', 'parent_organization_name', 'parent_organization_ext_id', 'recipient_name',
              'recipient_ext_id', 'recipient_party', 'recipient_type', 'recipient_state', 'recipient_state_held',
              'recipient_category', 'committee_name', 'committee_ext_id', 'committee_party',
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

    def read(self, request):
        return add_transaction_type_description(super(ContributionFilterHandler, self).read(request))


class ContributorGeoHandler(FilterHandler):
    fields = ['contributor_name', 'contributor_location', 'count', 'amount_total', 'amount_democrat', 'amount_republican']
    
    stmt = """
        select contributor_name, coalesce(m.name, c.contributor_zipcode), count(*), 
            sum(amount) as amount_total,
            sum(case when recipient_party = 'D' then amount else 0 end) as amount_democrat,
            sum(case when recipient_party = 'R' then amount else 0 end) as amount_republican
        from contribution_contribution c
        left join geo_zip z on c.contributor_zipcode = z.zipcode
        left join geo_msa m on z.msa_id = m.id
        where
            to_tsquery('datacommons', %s) @@ to_tsvector('datacommons', contributor_name)
        group by contributor_name, coalesce(m.name, c.contributor_zipcode), m.location
        order by ST_Distance(St_GeogFromText(%s), m.location)
        limit %s
    """
    
    def read(self, request):
        query = request.GET['query']
        (lat, lon) = (float(request.GET.get('lat')), float(request.GET.get('lon')))
        limit = int(request.GET.get('limit', '10'))
        
        raw_result = execute_top(self.stmt, query_to_ft_sql(query), "POINT(%s %s)" % (lon, lat), limit)
        
        labeled_result = [dict(zip(self.fields, row)) for row in raw_result]

        return labeled_result    

    
