from dcapi.common.handlers import FilterHandler
from dcapi.grants import filter_grants
from dcdata.grants.models import Grant


class GrantsFilterHandler(FilterHandler):
    model = Grant
    ordering = ['-fiscal_year','-amount_total']
    filename = 'grants'
        
    def queryset(self, params):
        return filter_grants(self._unquote(params))
    
