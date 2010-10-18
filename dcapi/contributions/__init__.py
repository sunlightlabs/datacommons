from dcapi.schema import Operator, Schema, InclusionField, OperatorField
from dcdata.contribution.models import Contribution
from dcdata.utils.sql import parse_date
from dcdata.utils.strings.transformers import build_remove_substrings, build_map_substrings
from django.db.models.query_utils import Q

"""
The schema used to search the Contribution model.

Defines the syntax of HTTP requests and how the requests are mapped into Django queries.
"""

EQUAL_OP = '='
LESS_THAN_OP = '<'
GREATER_THAN_OP = '>'
BETWEEN_OP = '><'

#
# convert all punctuation to simple whitespace
#

_ft_special_chars = "&|!():*"
_strip_postgres_ft_operators = build_map_substrings(dict(zip(_ft_special_chars, ' ' * len(_ft_special_chars))))

def _ft_terms(*searches):
    cleaned_searches = map(_strip_postgres_ft_operators, searches)
    return ' | '.join("(%s)" % ' & '.join(search.split()) for search in cleaned_searches)

def _ft_clause(column):
    return "to_tsvector('datacommons', %s) @@ to_tsquery('datacommons', %%s)" % column

def _ft_generator(query, column, *searches):
    return query.extra(where=[_ft_clause(column)], params=[_ft_terms(*searches)])

#
# filter generator methods
#

fields = []

# amount filter
    
def _amount_equal_generator(query, amount):
    return query.filter(amount=int(amount))
    
def _amount_less_than_generator(query, amount):
    return query.filter(amount__lte=int(amount))

def _amount_greater_than_generator(query, amount):
    return query.filter(amount__gte=int(amount))

def _amount_between_generator(query, lower, upper):
    return query.filter(amount__range=(int(lower), int(upper)))

fields.append(OperatorField('amount',
                Operator(EQUAL_OP, _amount_equal_generator),
                Operator(LESS_THAN_OP, _amount_less_than_generator),
                Operator(GREATER_THAN_OP, _amount_greater_than_generator),
                Operator(BETWEEN_OP, _amount_between_generator)))

# contributor industry filter

def _contributor_industry_in_generator(query, *industry):
    ors = Q()
    for ind in industry:
        if len(ind) == 5:
            ors = ors | Q(contributor_category=ind)
        elif len(ind) == 3:
            ors = ors | Q(contributor_category_order=ind)
        else:
            (catorder, catcode) = ind.split(',')
            if catcode:
                ors = ors | Q(contributor_category=catcode)
            else:
                ors = ors | Q(contributor_category_order=catorder)
    return query.filter(ors)

fields.append(InclusionField('contributor_industry', _contributor_industry_in_generator))

# contributor state filter

def _contributor_state_in_generator(query, *states):
    return query.filter(contributor_state__in=[state.upper() for state in states])
    
fields.append(InclusionField('contributor_state', _contributor_state_in_generator))

# cycle filter

def _cycle_in_generator(query, *cycles):
    def dual_cycles(cycles):
        for cycle in cycles:
            yield int(cycle) - 1
            yield int(cycle)
    return query.filter(cycle__in=[cycle for cycle in dual_cycles(cycles)])
    
fields.append(InclusionField('cycle', _cycle_in_generator))

# date filter

def _date_equal_generator(query, date):
    return query.filter(date=parse_date(date))

def _date_before_generator(query, date):
    return query.filter(date__lte=parse_date(date))
    
def _date_after_generator(query, date):
    return query.filter(date__gte=parse_date(date))
    
def _date_between_generator(query, first, second):
    return query.filter(date__range=(parse_date(first), parse_date(second)))

fields.append(OperatorField('date',
                Operator(EQUAL_OP, _date_equal_generator),
                Operator(LESS_THAN_OP, _date_before_generator),
                Operator(GREATER_THAN_OP, _date_after_generator),
                Operator(BETWEEN_OP, _date_between_generator)))

# for/against filter

def _for_against_generator(query, for_against):
    if for_against == 'for':
        query = query.exclude(transaction_type__in=('24a','24n'))
    elif for_against == 'against':
        query = query.filter(transaction_type__in=('24a','24n'))
    return query

fields.append(InclusionField('for_against', _for_against_generator))

# recipient state filter

def _recipient_state_in_generator(query, *states):
    return query.filter(recipient_state__in=[state.upper() for state in states])
    
fields.append(InclusionField('recipient_state', _recipient_state_in_generator))

# seat filter

def _seat_in_generator(query, *seats):
    return query.filter(seat__in=seats)
    
fields.append(InclusionField('seat', _seat_in_generator))

# transaction namespace (jurisdiction) filter

def _transaction_namespace_generator(query, *jurisdiction):
    return query.filter(transaction_namespace__in=jurisdiction)

fields.append(InclusionField('transaction_namespace', _transaction_namespace_generator))

# transaction type filter

def _transaction_type_in_generator(query, *transaction_types):
    return query.filter(transaction_type__in=transaction_types)
    
fields.append(InclusionField('transaction_type', _transaction_type_in_generator))

#
# name search fields
#

# commitee

def _committee_ft_generator(query, *searches):
    return _ft_generator(query, 'committee_name', *searches)

fields.append(InclusionField('committee_ft', _committee_ft_generator))

# contributor (organization, parent, employer, contributor)

def _contributor_ft_generator(query, *searches):
    terms = _ft_terms(*searches)
    clause = "(%s)" % " or ".join([_ft_clause('organization_name'), _ft_clause('parent_organization_name'), _ft_clause('contributor_employer'), _ft_clause('contributor_name')])
    return query.extra(where=[clause], params=[terms, terms, terms, terms])
    
fields.append(InclusionField('contributor_ft', _contributor_ft_generator))

# contributor ONLY

def _contributor_only_ft_generator(query, *searches):
    terms = _ft_terms(*searches)
    clause = "(%s)" % _ft_clause('contributor_name')
    return query.extra(where=[clause], params=[terms, terms, terms, terms])
    
fields.append(InclusionField('contributor_only_ft', _contributor_only_ft_generator))

# organization (organization, parent, employer)
        
def _organization_ft_generator(query, *searches):
    terms = _ft_terms(*searches)
    clause = "(%s)" % " or ".join([_ft_clause('organization_name'), _ft_clause('parent_organization_name'), _ft_clause('contributor_employer')])
    return query.extra(where=[clause], params=[terms, terms, terms])
    
fields.append(InclusionField('employer_ft', _organization_ft_generator)) # deprecated!!!!
fields.append(InclusionField('organization_ft', _organization_ft_generator))

# recipient

def _recipient_ft_generator(query, *searches):
    return _ft_generator(query, 'recipient_name', *searches)
    
fields.append(InclusionField('recipient_ft', _recipient_ft_generator))

# entity fields
# def _contributor_in_generator(query, *entities):    
#     return query.filter(Q(contributor_entity__in=entities) | Q(organization_entity__in=entities) | Q(parent_organization_entity__in=entities))
# def _organization_in_generator(query, *entities):
#     return query.filter(Q(organization_entity__in=entities) | Q(parent_organization_entity__in=entities))

# the final search schema

CONTRIBUTION_SCHEMA = Schema(*fields)

def filter_contributions(request):    
    return CONTRIBUTION_SCHEMA.build_filter(Contribution.objects, request).order_by()
