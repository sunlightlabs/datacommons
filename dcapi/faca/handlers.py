from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import FulltextField
from dcapi.schema import Schema
from dcdata.faca.models import FACARecord

FACA_SCHEMA = Schema(
    FulltextField('agency', ['agency_abbr', 'agency_name']),
    FulltextField('committee_name'),
    FulltextField('member_name'),
    FulltextField('affiliation'),
    
# todo: custom field type for active in year    

)


def filter_faca(request):
    return FACA_SCHEMA.build_filter(FACARecord.objects, request)


class FACAFilterHandler(FilterHandler):
    
    ordering = ['committee_name']
    filename = 'faca'
    model = FACARecord
    
    def queryset(self, params):
        return filter_faca(self._unquote(params))