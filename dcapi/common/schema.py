from dcapi.schema import OperatorField, Operator, Field
from dcdata.utils.strings.transformers import build_remove_substrings

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
        

class FulltextField(Field):
    def __init__(self, name, model_fields=None):
        super(FulltextField, self).__init__(name)
        self.model_fields = model_fields if model_fields else [name]
        self.clause = "(%s)" % " or ".join([_fulltext_clause(column) for column in self.model_fields])
                
    def apply(self, query, *searches):
        cleaned_searches = map(_strip_postgres_ft_operators, searches)
        terms =' | '.join("(%s)" % ' & '.join(search.split()) for search in cleaned_searches)
        return query.extra(where=[self.clause], params=[terms] * len(self.model_fields))
     

_strip_postgres_ft_operators = build_remove_substrings("&|!():*")

def _fulltext_clause(column):
    return """to_tsvector('datacommons', %s) @@ to_tsquery('datacommons', %%s)""" % column


