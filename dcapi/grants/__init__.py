from django.db.models.query_utils import Q
from dcapi.common.schema import fulltext_generator
from dcapi.schema import Operator, Schema, InclusionField, OperatorField
from dcdata.utils.sql import parse_date
from dcdata.grants.models import Grant

EQUAL_OP = '='
LESS_THAN_OP = '<'
GREATER_THAN_OP = '>'
BETWEEN_OP = '><'

AGENCY_FT_FIELD = 'agency_ft'
AMOUNT_TOTAL_FIELD = 'amount_total'
ASSISTANCE_TYPE_FIELD = 'assistance_type'
FISCAL_YEAR_FIELD = 'fiscal_year'
RECIPIENT_FT_FIELD = 'recipient_ft'
RECIPIENT_STATE_FIELD = 'recipient_state'
RECIPIENT_TYPE_FIELD = 'recipient_type'

# amount total generators

def _amount_total_equal_generator(query, amount):
    return query.filter(amount_total=int(amount))
        
def _amount_total_less_than_generator(query, amount):
    return query.filter(amount_total__lte=int(amount))
    
def _amount_total_greater_than_generator(query, amount):
    return query.filter(amount_total__gte=int(amount))
    
def _amount_total_between_generator(query, lower, upper):
    return query.filter(amount_total__range=(int(lower), int(upper)))

# full-text generators

def _agency_ft_generator(query, *searches):
    return fulltext_generator(query, 'agency_name', *searches)

def _recipient_ft_generator(query, *searches):
    return fulltext_generator(query, 'recipient_name', *searches)

# other generators

def _assistance_type_generator(query, *types):
    return query.filter(assistance_type__in=types)

def _fiscal_year_generator(query, *years):
    return query.filter(fiscal_year__in=years)
    
def _recipient_state_generator(query, *states):
    return query.filter(recipient_state__in=states)

def _recipient_type_generator(query, *types):
    return query.filter(recipient_type__in=types)

# SCHEMA

GRANTS_SCHEMA = Schema(
    InclusionField(AGENCY_FT_FIELD, _agency_ft_generator),
    InclusionField(ASSISTANCE_TYPE_FIELD, _assistance_type_generator),
    InclusionField(FISCAL_YEAR_FIELD, _fiscal_year_generator),
    InclusionField(RECIPIENT_FT_FIELD, _recipient_ft_generator),
    InclusionField(RECIPIENT_STATE_FIELD, _recipient_state_generator),
    InclusionField(RECIPIENT_TYPE_FIELD, _recipient_type_generator),
    OperatorField(AMOUNT_TOTAL_FIELD,
        Operator(EQUAL_OP, _amount_total_equal_generator),
        Operator(LESS_THAN_OP, _amount_total_less_than_generator),
        Operator(GREATER_THAN_OP, _amount_total_greater_than_generator),
        Operator(BETWEEN_OP, _amount_total_between_generator))
)

def filter_grants(request):
    q = GRANTS_SCHEMA.build_filter(Grant.objects, request).order_by()
    return q.select_related()