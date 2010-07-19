from django.db.models.query_utils import Q
from dcdata.utils.sql import parse_date
from dcdata.contracts.models import Contract
from dcapi.common.schema import fulltext_generator
from dcapi.schema import Operator, Schema, InclusionField, OperatorField

EQUAL_OP = '='
LESS_THAN_OP = '<'
GREATER_THAN_OP = '>'
BETWEEN_OP = '><'

# full-text agency generators

def _agency_ft_generator(query, *searches):
    return fulltext_generator(query, 'agency_name', *searches) # full-text

def _contracting_agency_ft_generator(query, *searches):
    return fulltext_generator(query, 'contracting_agency_name', *searches) # full-text

def _requesting_agency_ft_generator(query, *searches):
    return fulltext_generator(query, 'requesting_agency_name', *searches) # full-text

# agency id generators

def _agency_id_generator(query, *ids):
    return query.filter(agency_id__in=ids)
    
def _contracting_agency_id_generator(query, *ids):
    return query.filter(contracting_agency_id__in=ids)
    
def _requesting_agency_id_generator(query, *ids):
    return query.filter(requesting_agency_id__in=ids)

# vendor generators

def _vendor_ft_generator(query, *searches):
    return fulltext_generator(query, 'vendor_name', *searches) # full-text

def _vendor_city_ft_generator(query, *searches):
    return fulltext_generator(query, 'vendor_city', *searches) # full-text

def _vendor_state_generator(query, *ids):
    return query.filter(vendor_state__in=ids)
    
def _vendor_zipcode_generator(query, *ids):
    return query.filter(vendor_zipcode__in=ids)
    
def _vendor_district_generator(query, *ids):
    return query.filter(vendor_district__in=ids)
    
def _vendor_duns_generator(query, *ids):
    return query.filter(vendor_duns__in=ids)
    
def _vendor_parent_duns_generator(query, *ids):
    return query.filter(vendor_parent_duns__in=ids)

# place of performance generators    
    
def _place_district_generator(query, *ids):
    return query.filter(place_district__in=ids)
    
def _place_state_code_generator(query, *ids):
    return query.filter(place_state_code__in=ids)

# value generators

def _fiscal_year_generator(query, *years):
    return query.filter(fiscal_year__in=years)

# amount generators

class AmountGenerator(object):
    def __init__(self, field):
        self.field = field
    def generate(self, query, key, value):
        return query.filter(**{key: value})
    def equal(self, query, amount):
        return self.generate(query, self.field, int(amount))
    def less_than(self, query, amount):
        return self.generate(query, "%__lte" % self.field, int(amount))
    def greater_than(self, query, amount):
        return self.generate(query, "%__gte" % self.field, int(amount))
    def between(self, query, lower, upper):
        return self.generate(query, "%__range" % self.field, (int(lower), int(upper)))

obligated_amount_gen = AmountGenerator('obligated_amount')
current_amount_gen = AmountGenerator('current_amount')
maximum_amount_gen = AmountGenerator('maximum_amount')

# the schema!

CONTRACTS_SCHEMA = Schema(
    # fields
    InclusionField('agency_id', _agency_id_generator),
    InclusionField('agency_name', _agency_ft_generator),
    InclusionField('contracting_agency_id', _contracting_agency_id_generator),
    InclusionField('contracting_agency_name', _contracting_agency_ft_generator),
    InclusionField('fiscal_year', _fiscal_year_generator),
    InclusionField('place_distrct', _place_district_generator),
    InclusionField('place_state_code', _place_state_code_generator),
    InclusionField('requesting_agency_id', _requesting_agency_id_generator),
    InclusionField('requesting_agency_name', _requesting_agency_ft_generator),
    InclusionField('vendor_name', _vendor_ft_generator),
    InclusionField('vendor_city', _vendor_city_ft_generator),
    InclusionField('vendor_state', _vendor_state_generator),
    InclusionField('vendor_zipcode', _vendor_zipcode_generator),
    InclusionField('vendor_district', _vendor_district_generator),
    InclusionField('vendor_duns', _vendor_duns_generator),
    InclusionField('vendor_parent_duns', _vendor_parent_duns_generator),
    # amounts
    OperatorField('obligated_amount',
        Operator(EQUAL_OP, obligated_amount_gen.equal),
        Operator(LESS_THAN_OP, obligated_amount_gen.less_than),
        Operator(GREATER_THAN_OP, obligated_amount_gen.greater_than),
        Operator(BETWEEN_OP, obligated_amount_gen.between)),
    OperatorField('current_amount',
        Operator(EQUAL_OP, current_amount_gen.equal),
        Operator(LESS_THAN_OP, current_amount_gen.less_than),
        Operator(GREATER_THAN_OP, current_amount_gen.greater_than),
        Operator(BETWEEN_OP, current_amount_gen.between)),
    OperatorField('maximum_amount',
        Operator(EQUAL_OP, maximum_amount_gen.equal),
        Operator(LESS_THAN_OP, maximum_amount_gen.less_than),
        Operator(GREATER_THAN_OP, maximum_amount_gen.greater_than),
        Operator(BETWEEN_OP, maximum_amount_gen.between)),
)

def filter_contracts(request):
    q = CONTRACTS_SCHEMA.build_filter(Contract.objects, request).order_by()
    return q