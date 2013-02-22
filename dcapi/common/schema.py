
import itertools
import re

from django.db.models import Q
from django.db import connection

from dcapi.schema import OperatorField, Operator, Field
from dcdata.utils.strings.transformers import build_map_substrings

EQUAL_OP = '='
LESS_THAN_OP = '<'
GREATER_THAN_OP = '>'
BETWEEN_OP = '><'

class ComparisonField(OperatorField):
    def __init__(self, name, model_field=None, cast=None):
        super(ComparisonField, self).__init__(name,
            Operator(EQUAL_OP, self._equal),
            Operator(LESS_THAN_OP, self._less_than),
            Operator(GREATER_THAN_OP, self._greater_than),
            Operator(BETWEEN_OP, self._between)
        )
        
        self.field = model_field if model_field else name
        self.cast = cast if cast else lambda x: x
        
    def _generate(self, query, key, value):
        return query.filter(**{key: value})
    def _equal(self, query, amount):
        return self._generate(query, self.field, self.cast(amount))
    def _less_than(self, query, amount):
        return self._generate(query, "%s__lte" % self.field, self.cast(amount))
    def _greater_than(self, query, amount):
        return self._generate(query, "%s__gte" % self.field, self.cast(amount))
    def _between(self, query, lower, upper):
        return self._generate(query, "%s__range" % self.field, (self.cast(lower), self.cast(upper)))


class InclusionField(Field):
    def __init__(self, name, model_field=None):
        super(InclusionField, self).__init__(name)
        self.query_key = '%s__in' % (model_field if model_field else name)

    def apply(self, query, *args):
        return query.filter(**{self.query_key: args})
        

class IndustryField(Field):
    def __init__(self, name, model_field=None):
        super(IndustryField, self).__init__(name)
        self.model_field = model_field if model_field else name
        
    def _extract_cat_or_order(self, v):
        if ',' in v:
            (order, cat) = v.split(',')
            return cat if cat else order
        return v

    def _add_industry_clauses(self, query, categories, orders):
        join_condition = '%s=catcode' % self.model_field
        cat_clause = '%s in (%s)' % (self.model_field, ', '.join(["'%s'" % cat.upper() for cat in categories]))
        order_clause = 'catorder in (%s)' % ', '.join(["'%s'" % order.upper() for order in orders])
        
        if categories and orders:
            where_clause = "(%s or %s)" % (cat_clause, order_clause)
            return query.extra(tables=['agg_cat_map'], where=[where_clause, join_condition])
        
        if orders:
            return query.extra(tables=['agg_cat_map'], where=[order_clause, join_condition])
        
        if categories:
            return query.extra(where=[cat_clause])
        
        return query
    
    def apply(self, query, *industries):
        parsed_industries = [self._extract_cat_or_order(i) for i in industries]
        
        malformed_industries = [ind for ind in parsed_industries if len(ind) not in (3, 5)]
        if malformed_industries:
            raise ValueError("Arguments not valid industry categories or category orders: %s" % str(malformed_industries))
        
        orders = [order for order in parsed_industries if len(order)==3]
        cats = [cat for cat in parsed_industries if len(cat)==5]
            
        return self._add_industry_clauses(query, cats, orders)


_punctuation_to_spaces = dict([(c, ' ') for c in "\"'&|!():*\\"])
_strip_postgres_ft_operators = build_map_substrings(_punctuation_to_spaces)


class FulltextField(Field):
    def __init__(self, name, model_fields=None):
        super(FulltextField, self).__init__(name)
        self.model_fields = model_fields if model_fields else [name]
                
    def apply(self, query, *searches):
        ft_searches = [_format_ft_search(s) for s in searches]
        exact_searches = [_format_exact_search(s) for s in searches]

        where_clause = _search_clause(self.model_fields, [s is not None for s in exact_searches])

        params = dict([('ft_term_%s' % i, ft_searches[i]) for i in range(len(searches))])
        params.update(dict([('exact_term_%s' % i, exact_searches[i]) for i in range(len(searches))]))

        # note: have to explicitly call mogrify() to safely inject parameters
        # b/c Django's extra() method doesn't support dictionary interpolation.

        return query.extra(where=[connection.cursor().mogrify(where_clause, params)])


def _format_ft_search(search_string):
    return ' & '.join(_strip_postgres_ft_operators(search_string).split())

def _format_exact_search(search_string):
    m = re.search('^"(.*)"$', search_string)
    if m:
        return '%%' + m.group(1) + '%%'
    else:
        return None

def _search_clause(columns, has_exact_term):
        clauses = [
            _column_search_clause(column, i, exact)
            for (column, (i, exact)) in itertools.product(columns, [(i, has_exact_term[i]) for i in range(len(has_exact_term))])
        ]
        return "(%s)" % " or ".join(clauses)

def _column_search_clause(column, search_index, has_exact_term):
    ft_clause = "to_tsvector('datacommons', %s) @@ to_tsquery('datacommons', %%(ft_term_%s)s)" % (column, search_index)
    if has_exact_term:
        exact_clause = "%s ilike %%(exact_term_%s)s" % (column, search_index)
        return "(%s and %s)" % (ft_clause, exact_clause)
    else:
        return ft_clause


# these two methods are outdated as far as this package is concerned,
# but they're still used in MSAHandler.

def query_to_ft_sql(*searches):
    cleaned_searches = map(_strip_postgres_ft_operators, searches)
    return ' | '.join("(%s)" % ' & '.join(search.split()) for search in cleaned_searches)

def _fulltext_clause(column):
    return """to_tsvector('datacommons', %s) @@ to_tsquery('datacommons', %%s)""" % column


