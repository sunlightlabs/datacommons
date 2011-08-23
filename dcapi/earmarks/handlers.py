
from dcapi.common.handlers import DenormalizingFilterHandler
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
    FulltextField('city', ['earmarks_location.city']),
    FulltextField('member', ['earmarks_member.standardized_name', 'earmarks_member.raw_name']),
    FulltextField('recipient', ['earmarks_recipient.standardized_recipient', 'earmarks_recipient.raw_recipient']),
    
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
        
    return qs.order_by().distinct().select_related()
    

class EarmarkFilterHandler(DenormalizingFilterHandler):
    ordering = ['-fiscal_year', '-final_amount']
    filename = 'earmarks'
    
    simple_fields = [
        'fiscal_year',
        'final_amount',
        'budget_amount',
        'house_amount',
        'senate_amount',
        'omni_amount',
        'bill',
        'bill_section',
        'bill_subsection',
        'description',
        'notes',
        'presidential',
        'undisclosed',
    ]
    
    relation_fields = [
        'members',
        'locations',
        'recipients'
    ]
    
    def queryset(self, params):
        return filter_earmarks(self._unquote(params))

