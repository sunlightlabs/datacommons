from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.grants.models import Grant

GRANTS_SCHEMA = Schema(
    InclusionField('assistance_type'),
    InclusionField('fiscal_year'),
    InclusionField('recipient_state', 'recipient_state_code'),
    InclusionField('recipient_type'),
    
    FulltextField('agency_ft', ['agency_name']),
    FulltextField('recipient_ft', ['recipient_name']),

    ComparisonField('amount_total', 'total_funding_amount', cast=int)
)

def filter_grants(request):
    q = GRANTS_SCHEMA.build_filter(Grant.objects, request).order_by()
    return q.select_related()


class GrantsFilterHandler(FilterHandler):

    # imported_on is marked as an auto-generated field/non-editable,
    # so was getting dropped by Django's model_to_dict serialization,
    # but still required by the list of fields,
    # so we pass the list of fields we want directly instead

    fields = Grant._meta.get_all_field_names()
    fields.remove('imported_on')


    ordering = ['-fiscal_year','-total_funding_amount']
    filename = 'grants'
        
    def queryset(self, params):
        return filter_grants(self._unquote(params))
    
