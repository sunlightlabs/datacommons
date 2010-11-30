from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.grants.models import Grant

GRANTS_SCHEMA = Schema(
    InclusionField('assistance_type'),
    InclusionField('fiscal_year'),
    InclusionField('recipient_state'),
    InclusionField('recipient_type'),
    
    FulltextField('agency_ft', ['agency_name']),
    FulltextField('recipient_ft', ['recipient_name']),

    ComparisonField('amount_total', cast=int)
)

def filter_grants(request):
    q = GRANTS_SCHEMA.build_filter(Grant.objects, request).order_by()
    return q.select_related()


class GrantsFilterHandler(FilterHandler):
    model = Grant
    ordering = ['-fiscal_year','-amount_total']
    filename = 'grants'
        
    def queryset(self, params):
        return filter_grants(self._unquote(params))
    
