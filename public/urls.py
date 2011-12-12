from dcapi.contracts.urls import contractsfilter_handler
from dcapi.contributions.urls import contributionfilter_handler
from dcapi.earmarks.urls import earmarkfilter_handler
from dcapi.grants.urls import grantsfilter_handler
from dcapi.lobbying.urls import lobbyingfilter_handler
from dcapi.contractor_misconduct.urls import contractor_misconduct_filter_handler
from dcapi.epa.urls import epafilter_handler
from dcapi.faca.urls import facafilter_handler
from dcapi.contributions.bundling.urls import bundlingfilter_handler

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('public.views',        
    # contracts
    url(r'^data/contracts/download/$', 'search_download', {'search_resource': contractsfilter_handler},  name="data_contracts_download"),
    url(r'^data/contracts/$', 'search_preview', {'search_resource': contractsfilter_handler}, name="data_contracts"),
    url(r'^data/contracts/count/$', 'search_count', {'search_resource': contractsfilter_handler}, name="data_contracts_count"),
    
    # contributions
    url(r'^data/contributions/download/$', 'search_download', {'search_resource': contributionfilter_handler},  name="data_contributions_download"),
    url(r'^data/contributions/$', 'search_preview', {'search_resource': contributionfilter_handler}, name="data_contributions"),
    url(r'^data/contributions/count/$', 'search_count', {'search_resource': contributionfilter_handler}, name="data_contributions_count"),
    
    # earmarks
    url(r'^data/download/earmarks/$', 'search_download', {'search_resource': earmarkfilter_handler},  name="data_earmarks_download"),
    url(r'^data/earmarks/$', 'search_preview', {'search_resource': earmarkfilter_handler}, name="data_earmarks"),
    url(r'^data/earmarks/count/$', 'search_count', {'search_resource': earmarkfilter_handler}, name="data_earmarks_count"),
     
    # grants
    url(r'^data/grants/download/$', 'search_download', {'search_resource': grantsfilter_handler},  name="data_grants_download"),
    url(r'^data/grants/$', 'search_preview', {'search_resource': grantsfilter_handler}, name="data_grants"),
    url(r'^data/grants/count/$', 'search_count', {'search_resource': grantsfilter_handler}, name="data_grants_count"),

    # lobbying
    url(r'^data/lobbying/download/$', 'search_download', {'search_resource': lobbyingfilter_handler},  name="data_lobbying_download"),
    url(r'^data/lobbying/$', 'search_preview', {'search_resource': lobbyingfilter_handler}, name="data_lobbying"),
    url(r'^data/lobbying/count/$', 'search_count', {'search_resource': lobbyingfilter_handler}, name="data_lobbying_count"),

    # contractor_misconduct
    url(r'^data/contractor_misconduct/download/$', 'search_download', {'search_resource': contractor_misconduct_filter_handler},  name="data_contractor_misconduct_download"),
    url(r'^data/contractor_misconduct/$', 'search_preview', {'search_resource': contractor_misconduct_filter_handler}, name="data_contractor_misconduct"),
    url(r'^data/contractor_misconduct/count/$', 'search_count', {'search_resource': contractor_misconduct_filter_handler}, name="data_contractor_misconduct_count"),

    # epa_echo
    url(r'^data/epa_echo/download/$', 'search_download', {'search_resource': epafilter_handler},  name="data_epa_echo_download"),
    url(r'^data/epa_echo/$', 'search_preview', {'search_resource': epafilter_handler}, name="data_epa_echo"),
    url(r'^data/epa_echo/count/$', 'search_count', {'search_resource': epafilter_handler}, name="data_epa_echo_count"),

    # faca
    url(r'^data/faca/download/$', 'search_download', {'search_resource': facafilter_handler},  name="data_faca_download"),
    url(r'^data/faca/$', 'search_preview', {'search_resource': facafilter_handler}, name="data_faca"),
    url(r'^data/faca/count/$', 'search_count', {'search_resource': facafilter_handler}, name="data_faca_count"),

    # bundled contributions
    url(r'^data/contributions/bundled/download/$', 'search_download', {'search_resource': bundlingfilter_handler},  name="data_bundling_download"),
    url(r'^data/contributions/bundled/$', 'search_preview', {'search_resource': bundlingfilter_handler}, name="data_bundling"),
    url(r'^data/contributions/bundled/count/$', 'search_count', {'search_resource': bundlingfilter_handler}, name="data_bundling_count"),        
)