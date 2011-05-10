from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.pogo.models import ContractorMisconduct

CONTRACTOR_MISCONDUCT_SCHEMA = Schema(
    InclusionField('date_year'),

    ComparisonField('penalty_amount', 'penalty_amount', cast=int),

    FulltextField('contractor'),
    FulltextField('enforcement_agency_ft'),
    FulltextField('instance'),
    FulltextField('contracting_party'),

)


def filter_contractor_misconduct(request):
    return CONTRACTOR_MISCONDUCT_SCHEMA.build_filter(ContractorMisconduct.objects, request).order_by()


class ContractorMisconductFilterHandler(FilterHandler):
    model = ContractorMisconduct
    ordering = ['-date','-disposition']
    filename = 'contractor_misconduct'
        
    def queryset(self, params):
        return filter_contractor_misconduct(self._unquote(params))
    

