from dcapi.common.handlers import FilterHandler
from dcapi.contracts import filter_contracts
from dcdata.contracts.models import Contract


class ContractsFilterHandler(FilterHandler):
    model = Contract
    ordering = ['-fiscal_year','-current_amount']
        
    def queryset(self, params):
        return filter_contracts(self._unquote(params))
    
