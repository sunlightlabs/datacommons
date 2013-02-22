from django.db.models import Q

from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import FulltextField
from dcapi.schema import Schema, FunctionField
from dcdata.faca.models import FACARecord


def _year_generator(q, *years):
    or_query = Q()
    for year in years:
        or_query.add(Q(start_date__lte="%s-12-31" % year, end_date__gte="%s-01-01" % year), Q.OR)
    
    return q.filter(or_query)


FACA_SCHEMA = Schema(
    FulltextField('agency_name', ['agency_abbr', 'agency_name']),
    FulltextField('committee_name'),
    FulltextField('member_name'),
    FulltextField('affiliation'),
    FunctionField('year', _year_generator)
)


def filter_faca(request):
    return FACA_SCHEMA.build_filter(FACARecord.objects, request)


class FACAFilterHandler(FilterHandler):
    
    ordering = ['committee_name']
    filename = 'faca'
    model = FACARecord
    
    def queryset(self, params):
        return filter_faca(self._unquote(params))
