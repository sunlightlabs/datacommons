from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import FulltextField
from dcapi.schema import Schema
from dcdata.contribution.models import LobbyistBundlingDenormalized


BUNDLING_SCHEMA = Schema(
    FulltextField('recipient_name', ['committee_name', 'standardized_recipient_name']),
    FulltextField('lobbyist_name', ['standardized_lobbyist_name', 'standardized_firm_name', 'bundler_name', 'bundler_employer']),
)

def filter_bundling(request):
    return BUNDLING_SCHEMA.build_filter(LobbyistBundlingDenormalized.objects, request)


class BundlingFilterHandler(FilterHandler):
    fields = [f.name for f in LobbyistBundlingDenormalized._meta.fields]
    model = LobbyistBundlingDenormalized
    ordering = ['committee_name', 'bundler_name', '-report_year']
    filename = 'lobbyist_bundled_contributions'

    def queryset(self, params):
        return filter_bundling(self._unquote(params))


