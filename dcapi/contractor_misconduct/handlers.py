from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.pogo.models import Misconduct

CONTRACTOR_MISCONDUCT_SCHEMA = Schema(
    InclusionField('date_year'),

    ComparisonField('penalty_amount', 'penalty_amount', cast=int),

    FulltextField('name_ft', ['name']),
    FulltextField('enforcement_agency_ft'),
    FulltextField('instance_ft'),
    FulltextField('contracting_party_ft'),

)


def filter_contractor_misconduct(request):
    return CONTRACTOR_MISCONDUCT_SCHEMA.build_filter(Misconduct.objects, request).order_by()


class ContractorMisconductFilterHandler(FilterHandler):
    #fields = ( ('contractor', ('name',),), 'instance', 'penalty_amount', 'contracting_party', 'court_type', 'date', 'date_significance', 'date_year', 'disposition', 'enforcement_agency', 'misconduct_type', 'synopsis')
    model = Misconduct
    ordering = ['-date','-disposition']
    filename = 'contractor_misconduct'

    def queryset(self, params):
        return filter_contractor_misconduct(self._unquote(params))


