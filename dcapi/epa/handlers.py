from dcapi.common.handlers import DenormalizingFilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.epa import models



EPA_SCHEMA = Schema(
    InclusionField('court_enforcement_no'),

    
    FulltextField('enforcement_name', ['enfornm']),
    
#    ComparisonField('amount', 'final_amount'),
)


def filter_epa(request):
    qs = EPA_SCHEMA.build_filter(models.CaseIdentifier.objects, request)

    # filters do nothing--just here to force the join that's needed for the fulltext search
#    if 'city' in request:
#        qs = qs.filter(locations__city__isnull=False)
       
    return qs.order_by().distinct().select_related()


class EPAFilterHandler(DenormalizingFilterHandler):
    # todo: ordering should change
    ordering = ['court_enforcement_no']
    filename = 'epa'
    
    simple_fields = [
        'court_enforcement_no',
        'enforcement_name',
    ]
    
    relation_fields = [
    ]
    
    def queryset(self, params):
        return filter_epa(self._unquote(params))
