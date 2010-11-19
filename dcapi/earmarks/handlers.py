
from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, ComparisonField, FulltextField
from dcapi.schema import Schema
from dcdata.earmarks.models import Earmark


EARMARKS_SCHEMA = Schema(
    InclusionField('year', 'fiscal_year'),
    InclusionField('locations__state'),
    InclusionField('member_party', ['members__party']),
    InclusionField('member_state', ['members__state']),
    
    FulltextField('bill', ['bill', 'bill_section', 'bill_subsection']),
    FulltextField('description', ['earmarks_earmark.description', 'notes']),
    FulltextField('locations__city'),
    FulltextField('member', ['members__standardized_name', 'members__raw_name']),
    FulltextField('recipient', ['recipients__standardized_recipient', 'recipients__raw_recipient']),
    
    ComparisonField('amount', 'final_amount'),
)

def filter_earmarks(request):
    return EARMARKS_SCHEMA.build_filter(Earmark.objects, request).order_by().select_related()
    

EARMARK_FIELDS = [
    'fiscal_year',
    'final_amount',
    'bill',
    'description'
]

class EarmarkFilterHandler(FilterHandler):
    model = Earmark
    ordering = ['-fiscal_year', '-final_amount']
    filename = 'earmarks'
    fields = EARMARK_FIELDS
    
    def queryset(self, params):
        return filter_earmarks(self._unquote(params))

