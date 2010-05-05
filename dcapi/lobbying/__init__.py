from django.db.models.query_utils import Q
from dcdata.utils.sql import parse_date
from dcdata.utils.strings.transformers import build_remove_substrings
from dcdata.lobbying.models import Lobbying
from dcapi.schema import Operator, Schema, InclusionField, OperatorField

EQUAL_OP = '='
LESS_THAN_OP = '<'
GREATER_THAN_OP = '>'
BETWEEN_OP = '><'

TRANSACTION_ID_FIELD = 'transaction_id'
TRANSACTION_TYPE_FIELD = 'transaction_type'

CLIENT_FT_FIELD = 'client_ft'
CLIENT_PARENT_FT_FIELD = 'client_parent_ft'
LOBBYIST_FT_FIELD = 'lobbyist_ft'
REGISTRANT_FT_FIELD = 'registrant_ft'

CLIENT_EXT_ID = 'client_ext_id'
LOBBYIST_EXT_ID = 'lobbyist_ext_id'
CANDIDATE_EXT_ID = 'candidate_ext_id'

AMOUNT_FIELD = 'amount'
ISSUE_FIELD = 'issue'
FILING_TYPE_FIELD = 'filing_type'
YEAR_FIELD = 'year'
LOBBYIST_IS_REP = 'lobbyist_is_rep'

# utility generators

def _ft_generator(query, column, *searches):
    return query.extra(where=[_ft_clause(column)], params=[_ft_terms(*searches)])

_strip_postgres_ft_operators = build_remove_substrings("&|!():*")

def _ft_terms(*searches):
    cleaned_searches = map(_strip_postgres_ft_operators, searches)
    return ' | '.join("(%s)" % ' & '.join(search.split()) for search in cleaned_searches)

def _ft_clause(column):
    return """to_tsvector('datacommons', %s) @@ to_tsquery('datacommons', %%s)""" % column

#
# generators

def _transaction_id_in_generator(query, *transaction_ids):
    return query.filter(transaction_id__in=transaction_ids)

def _transaction_type_in_generator(query, *transaction_types):
    return query.filter(transaction_type__in=transaction_types)

def _year_in_generator(query, *years):
    return query.filter(year__in=years)

def _filing_type_in_generator(query, *filing_types):
    return query.filter(filing_type__in=filing_types)

def _issue_in_generator(query, *issues):
    return query.filter(issues__general_issue_code__in=issues)

def _lobbyist_is_rep_generator(query, value):
    return query.filter(lobbyists__member_of_congress=True)

# external ids
def _client_ext_id_generator(query, *ids):
    return query.filter(client_ext_id__in=ids)

def _lobbyist_ext_id_generator(query, *ids):
    return query.filter(lobbyists__lobbyist_ext_id__in=ids)

def _candidate_ext_id_generator(query, *ids):
    return query.filter(lobbyists__candidate_ext_id__in=ids)

# amount generators
def _amount_equal_generator(query, amount):
    return query.filter(amount=int(amount))
        
def _amount_less_than_generator(query, amount):
    return query.filter(amount__lte=int(amount))
    
def _amount_greater_than_generator(query, amount):
    return query.filter(amount__gte=int(amount))
    
def _amount_between_generator(query, lower, upper):
    return query.filter(amount__range=(int(lower), int(upper)))

# full text generators
def _client_ft_generator(query, *searches):
    return _ft_generator(query, 'client_name', *searches)

def _client_parent_ft_generator(query, *searches):
    return _ft_generator(query, 'client_parent_name', *searches)

def _lobbyist_ft_generator(query, *searches):
    return _ft_generator(query, 'lobbyist_name', *searches)

def _registrant_ft_generator(query, *searches):
    return _ft_generator(query, 'registrant_name', *searches)

    
LOBBYING_SCHEMA = Schema(
    InclusionField(TRANSACTION_ID_FIELD, _transaction_id_in_generator),
    InclusionField(TRANSACTION_TYPE_FIELD, _transaction_type_in_generator),
    InclusionField(FILING_TYPE_FIELD, _filing_type_in_generator),
    InclusionField(YEAR_FIELD, _year_in_generator),
    InclusionField(ISSUE_FIELD, _issue_in_generator),
    InclusionField(LOBBYIST_IS_REP, _lobbyist_is_rep_generator),
    # external ids
    InclusionField(CLIENT_EXT_ID, _client_ext_id_generator),
    InclusionField(LOBBYIST_EXT_ID, _lobbyist_ext_id_generator),
    InclusionField(CANDIDATE_EXT_ID, _candidate_ext_id_generator),
    # full text fields
    InclusionField(CLIENT_FT_FIELD, _client_ft_generator),
    InclusionField(CLIENT_PARENT_FT_FIELD, _client_parent_ft_generator),
    InclusionField(LOBBYIST_FT_FIELD, _lobbyist_ft_generator),
    InclusionField(REGISTRANT_FT_FIELD, _registrant_ft_generator),
    # operator fields
    OperatorField(AMOUNT_FIELD,
        Operator(EQUAL_OP, _amount_equal_generator),
        Operator(LESS_THAN_OP, _amount_less_than_generator),
        Operator(GREATER_THAN_OP, _amount_greater_than_generator),
        Operator(BETWEEN_OP, _amount_between_generator)))

def filter_lobbying(request):
    q = LOBBYING_SCHEMA.build_filter(Lobbying.objects, request).order_by()
    if 'lobbyist_ft' in request:
        q = q.filter(lobbyists__lobbyist_name__isnull=False)
    return q.select_related()