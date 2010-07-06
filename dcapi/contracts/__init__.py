from django.db.models.query_utils import Q
from dcdata.utils.sql import parse_date
from dcdata.utils.strings.transformers import build_remove_substrings
from dcdata.contracts.models import Contract
from dcapi.schema import Operator, Schema, InclusionField, OperatorField

EQUAL_OP = '='
LESS_THAN_OP = '<'
GREATER_THAN_OP = '>'
BETWEEN_OP = '><'

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
    InclusionField('fiscal_year', _fiscal_year_generator),
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
    return q.select_related()