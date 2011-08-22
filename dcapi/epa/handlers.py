from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import InclusionField, FulltextField, ComparisonField
from dcapi.schema import Schema
from dcdata.epa import models
from dcdata.epa.models import DenormalizedAction



EPA_SCHEMA = Schema(
    InclusionField('case_num'),

    FulltextField('case_name'),
    FulltextField('defendants', ['defendants']),
    FulltextField('locations', ['locations']),
    
    ComparisonField('penalty'),
    ComparisonField('first_date'),
    ComparisonField('last_date'),
)


def filter_epa(request):
    qs = EPA_SCHEMA.build_filter(models.DenormalizedAction.objects, request)

    # filters do nothing--just here to force the join that's needed for the fulltext search
#    if 'city' in request:
#        qs = qs.filter(locations__city__isnull=False)
       
    return qs.order_by().distinct().select_related()


class EPAFilterHandler(FilterHandler):
    # todo: ordering should change
    ordering = ['-penalty']
    filename = 'epa'
    model = DenormalizedAction
    
    def queryset(self, params):
        return filter_epa(self._unquote(params))
