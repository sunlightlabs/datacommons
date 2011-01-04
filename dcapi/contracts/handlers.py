from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.contracts.models import Contract

CONTRACTS_SCHEMA = Schema(
    InclusionField('agency_id'),
    InclusionField('contracting_agency_id'),
    InclusionField('fiscal_year'),
    InclusionField('place_distrct'),
    InclusionField('place_state', 'place_state_code'),
    InclusionField('requesting_agency_id'),
    InclusionField('vendor_state'),
    InclusionField('vendor_zipcode'),
    InclusionField('vendor_district'),
    InclusionField('vendor_duns'),
    InclusionField('vendor_parent_duns'),

    FulltextField('agency_name'),
    FulltextField('contracting_agency_name'),
    FulltextField('requesting_agency_name'),
    FulltextField('vendor_name'),
    FulltextField('vendor_city'),

    ComparisonField('obligated_amount', cast=int),
    ComparisonField('current_amount', cast=int),
    ComparisonField('maximum_amount', cast=int)
)


def filter_contracts(request):
    return CONTRACTS_SCHEMA.build_filter(Contract.objects, request).order_by()


class ContractsFilterHandler(FilterHandler):
    model = Contract
    ordering = ['-fiscal_year','-current_amount']
    filename = 'contracts'
        
    def queryset(self, params):
        return filter_contracts(self._unquote(params))
    
