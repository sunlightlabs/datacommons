from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.pogo.models import Misconduct

CONTRACTOR_MISCONDUCT_SCHEMA = Schema(
    InclusionField('date_year'),

    ComparisonField('penalty_amount', 'penalty_amount', cast=int),

    FulltextField('contractor', ['pogo_contractor.name']),
    FulltextField('enforcement_agency'),
    FulltextField('instance'),
    FulltextField('contracting_party'),
)


def filter_contractor_misconduct(request):
    q = CONTRACTOR_MISCONDUCT_SCHEMA.build_filter(Misconduct.objects, request).order_by()

    # filter does nothing--it's here to force the join
    if 'contractor' in request:
        q = q.filter(contractor__name__isnull=False)

    return q.distinct().select_related()



class ContractorMisconductFilterHandler(FilterHandler):
    model = Misconduct
    ordering = ['-penalty_amount', '-date']
    filename = 'contractor_misconduct'


    def queryset(self, params):
        return filter_contractor_misconduct(self._unquote(params))


    # this flattens out the nested contractor record to come through as 'contractor': 'Company XYZ'
    @classmethod
    def contractor(cls, item):
        return item.contractor.name

