
from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, ComparisonField, FulltextField
from dcapi.schema import Schema
from dcdata.earmarks.models import Earmark


EARMARKS_SCHEMA = Schema(
    InclusionField('year', 'fiscal_year'),
    InclusionField('state', 'locations__state'),
    InclusionField('member_party', 'members__party'),
    InclusionField('member_state', 'members__state'),
    
    FulltextField('bill', ['bill', 'bill_section', 'bill_subsection']),
    FulltextField('description', ['earmarks_earmark.description', 'notes']),
    # the following three fulltext searches on related models don't work
    FulltextField('city'),
    FulltextField('member', ['standardized_name', 'raw_name']),
    FulltextField('recipient', ['standardized_recipient', 'raw_recipient']),
    
    ComparisonField('amount', 'final_amount'),
)

def filter_earmarks(request):
    qs = EARMARKS_SCHEMA.build_filter(Earmark.objects, request)
    
    # filters do nothing--just here to force the join that's needed for the fulltext search
    if 'city' in request:
        qs = qs.filter(locations__city__isnull=False)
    if 'member' in request:
        qs = qs.filter(members__raw_name__isnull=False)
    if 'recipient' in request:
        qs = qs.filter(recipients__raw_recipient__isnull=False)  
        
    return qs.order_by().select_related()
    
    
SIMPLE_FIELDS = [
    'fiscal_year',
    'final_amount',
    'bill',
    'description',
]

RELATION_FIELDS = [
    'members',
    'locations',
    'recipients'
]

EARMARK_FIELDS = SIMPLE_FIELDS + RELATION_FIELDS


class EarmarkFilterHandler(FilterHandler):
    ordering = ['-fiscal_year', '-final_amount']
    filename = 'earmarks'
    fields = EARMARK_FIELDS
    
    def _denormalize(self, earmark):
        result = dict((field, getattr(earmark, field)) for field in SIMPLE_FIELDS)
        
        for relation in RELATION_FIELDS:
            result[relation] = "; ".join(str(o) for o in getattr(earmark, relation).all())
        
        return result
        
    def queryset(self, params):
        return filter_earmarks(self._unquote(params))

    def read(self, request):
        for earmark in super(EarmarkFilterHandler, self).read(request):
            yield self._denormalize(earmark)

