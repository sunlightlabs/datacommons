
from dcapi.aggregates.contributions.handlers import OrgRecipientsHandler, \
    PolContributorsHandler, IndivOrgRecipientsHandler, IndivPolRecipientsHandler, \
    SectorsHandler, IndustriesHandler, UnknownIndustriesHandler, PolLocalBreakdownHandler, \
    PolContributorTypeBreakdownHandler, OrgLevelBreakdownHandler, \
    OrgPartyBreakdownHandler, IndivPartyBreakdownHandler, SparklineHandler, \
    SparklineByPartyHandler, TopPoliticiansByReceiptsHandler,  \
    TopIndividualsByContributionsHandler, TopOrganizationsByContributionsHandler, \
    TopIndustriesByContributionsHandler, IndustryOrgHandler, \
    ContributionAmountHandler, OrgPACRecipientsHandler
from dcapi.aggregates.contributions.bundle_handlers import BundleHandler, \
    RecipientExplorerHandler, FirmExplorerHandler, DetailExplorerHandler
from dcapi.aggregates.lobbying.handlers import OrgRegistrantsHandler, \
    OrgIssuesHandler, OrgBillsHandler, OrgLobbyistsHandler, \
    IndivRegistrantsHandler, IndivIssuesHandler, IndivClientsHandler, \
    RegistrantIssuesHandler, RegistrantBillsHandler, RegistrantClientsHandler, \
    RegistrantLobbyistsHandler
from dcapi.aggregates.spending.handlers import OrgFedSpendingHandler
from dcapi.aggregates.earmarks.handlers import TopEarmarksHandler,\
    LocalEarmarksHandler
from dcapi.aggregates.pogo.handlers import TopContractorMisconductHandler
from dcapi.aggregates.epa.handlers import TopViolationActionsHandler
from dcapi.aggregates.regulations.handlers import RegulationsTextHandler, \
    RegulationsSubmitterHandler, RegulationsDocketTextHandler, \
    RegulationsDocketSubmitterHandler
from dcapi.aggregates.fec.handlers import CandidateSummaryHandler, CandidateStateHandler, \
    CandidateTimelineHandler, CandidateItemizedDownloadHandler
from dcapi.aggregates.independentexpenditures.handlers import CandidateIndExpHandler, CommitteeIndExpHandler

from django.conf.urls.defaults import patterns, url
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource
from dcapi.aggregates.faca.handlers import FACAAgenciesHandler,\
    FACACommitteeMembersHandler
# We are using the default JSONEmitter so no need to explicitly
# register it. However, unregister those we don't need.
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }


urlpatterns = patterns('',

    url(r'^(pol|org|indiv)/(?P<entity_id>[a-f0-9]{32})/sparkline_by_party.(?P<emitter_format>.+)$',
        Resource(SparklineByPartyHandler, **ad)),

    url(r'^(pol|org|indiv)/(?P<entity_id>[a-f0-9]{32})/sparkline.(?P<emitter_format>.+)$',
        Resource(SparklineHandler, **ad)),

    # amount contributed by one entity to another
    url(r'^recipient/(?P<recipient_entity>[a-f0-9]{32})/contributor/(?P<contributor_entity>[a-f0-9]{32})/amount.(?P<emitter_format>.+)$',
        Resource(ContributionAmountHandler, **ad)),

    # contributors to a single politician
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/contributors\.(?P<emitter_format>.+)$',
        Resource(PolContributorsHandler, **ad)),

    # contributions to a single politician, broken down by sector
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/contributors/sectors\.(?P<emitter_format>.+)$',
        Resource(SectorsHandler, **ad)),

    # contributions to a single politician, broken down by industry
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/contributors/industries\.(?P<emitter_format>.+)$',
        Resource(IndustriesHandler, **ad)),

    # contributions to a single politician from unknown industries
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/contributors/industries_unknown\.(?P<emitter_format>.+)$',
        Resource(UnknownIndustriesHandler, **ad)),

    # contributions to a single politician, broken down to show percentages
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/contributors/local_breakdown\.(?P<emitter_format>.+)$',
        Resource(PolLocalBreakdownHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/contributors/type_breakdown\.(?P<emitter_format>.+)$',
        Resource(PolContributorTypeBreakdownHandler, **ad)),

    # top N politicians by receipts for a cycle
    url(r'^pols/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopPoliticiansByReceiptsHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/earmarks\.(?P<emitter_format>.+)$',
        Resource(TopEarmarksHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/earmarks/local_breakdown\.(?P<emitter_format>.+)$',
        Resource(LocalEarmarksHandler, **ad)),

    # recipients from a single individual, broken down to show percentages
    url(r'^indiv/(?P<entity_id>[a-f0-9]{32})/recipients/party_breakdown\.(?P<emitter_format>.+)$',
        Resource(IndivPartyBreakdownHandler, **ad)),

    # recipients from a single individual
    url(r'^indiv/(?P<entity_id>[a-f0-9]{32})/recipient_orgs\.(?P<emitter_format>.+)$',
        Resource(IndivOrgRecipientsHandler, **ad)),

    url(r'^indiv/(?P<entity_id>[a-f0-9]{32})/recipient_pols\.(?P<emitter_format>.+)$',
        Resource(IndivPolRecipientsHandler, **ad)),

    # lobbying - registrants this individual lobbied (worked) for
    url(r'indiv/(?P<entity_id>[a-f0-9]{32})/registrants\.(?P<emitter_format>.+)$',
        Resource(IndivRegistrantsHandler, **ad)),

    # issues an individual lobbied on
    url(r'indiv/(?P<entity_id>[a-f0-9]{32})/issues\.(?P<emitter_format>.+)$',
        Resource(IndivIssuesHandler, **ad)),

    # clients of the firms this individual lobbied with
    url(r'indiv/(?P<entity_id>[a-f0-9]{32})/clients\.(?P<emitter_format>.+)$',
        Resource(IndivClientsHandler, **ad)),

    # top N individuals by contributions for a cycle
    url(r'^indivs/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopIndividualsByContributionsHandler, **ad)),

    # recipients from a single org//pac
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/recipients\.(?P<emitter_format>.+)$',
        Resource(OrgRecipientsHandler, **ad)),

    # pac recipients from an org
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/recipient_pacs\.(?P<emitter_format>.+)$',
        Resource(OrgPACRecipientsHandler, **ad)),

    # recipients from a single org, broken down to show percentages
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/recipients/party_breakdown\.(?P<emitter_format>.+)$',
        Resource(OrgPartyBreakdownHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/recipients/level_breakdown\.(?P<emitter_format>.+)$',
        Resource(OrgLevelBreakdownHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/registrants\.(?P<emitter_format>.+)$',
        Resource(OrgRegistrantsHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/earmarks\.(?P<emitter_format>.+)$',
        Resource(TopEarmarksHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/contractor_misconduct\.(?P<emitter_format>.+)$',
        Resource(TopContractorMisconductHandler, **ad)),
        
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/regulations_text\.(?P<emitter_format>.+)$',
        Resource(RegulationsTextHandler, **ad)),
    
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/regulations_text_by_docket/(?P<docket_id>[-_A-Z0-9]+)\.(?P<emitter_format>.+)$',
        Resource(RegulationsDocketTextHandler, **ad)),
    
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/regulations_submitter\.(?P<emitter_format>.+)$',
        Resource(RegulationsSubmitterHandler, **ad)),
    
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/regulations_submitter_by_docket/(?P<docket_id>[-_A-Z0-9]+)\.(?P<emitter_format>.+)$',
        Resource(RegulationsDocketSubmitterHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/epa_enforcement_actions\.(?P<emitter_format>.+)$',
        Resource(TopViolationActionsHandler, **ad)),

    # issues an org hired people to lobby on
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/issues\.(?P<emitter_format>.+)',
        Resource(OrgIssuesHandler, **ad)),

    # bills an org hired people to lobby on
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/bills\.(?P<emitter_format>.+)',
        Resource(OrgBillsHandler, **ad)),

    # lobbyists who worked with this org.
    url(r'org/(?P<entity_id>[a-f0-9]{32})/lobbyists\.(?P<emitter_format>.+)',
        Resource(OrgLobbyistsHandler, **ad)),

    url(r'org/(?P<entity_id>[a-f0-9]{32})/registrant/issues\.(?P<emitter_format>.+)',
        Resource(RegistrantIssuesHandler, **ad)),

    url(r'org/(?P<entity_id>[a-f0-9]{32})/registrant/bills\.(?P<emitter_format>.+)',
        Resource(RegistrantBillsHandler, **ad)),

    url(r'org/(?P<entity_id>[a-f0-9]{32})/registrant/clients\.(?P<emitter_format>.+)',
        Resource(RegistrantClientsHandler, **ad)),

    url(r'org/(?P<entity_id>[a-f0-9]{32})/registrant/lobbyists\.(?P<emitter_format>.+)',
        Resource(RegistrantLobbyistsHandler, **ad)),

    # top N organizations by contributions for a cycle
    url(r'^orgs/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopOrganizationsByContributionsHandler, **ad)),

    # top N industries by contributions for a cycle
    url(r'^industries/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopIndustriesByContributionsHandler, **ad)),

    # Grants and Contracts Spending
    url(r'^org/(?P<entity_id>[a-f0-9]{32})/fed_spending\.(?P<emitter_format>.+)',
        Resource(OrgFedSpendingHandler, **ad)),

    # organizations in an industry
    url(r'^industry/(?P<entity_id>[a-f0-9]{32})/orgs\.(?P<emitter_format>.+)$',
        Resource(IndustryOrgHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/faca\.(?P<emitter_format>.+)$',
        Resource(FACAAgenciesHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/faca/(?P<agency>.+)\.(?P<emitter_format>.+)$',
        Resource(FACACommitteeMembersHandler, **ad)),

    # bundling
    url(r'^(org|indiv|pol)/(?P<entity_id>[a-f0-9]{32})/bundles\.(?P<emitter_format>.+)$',
            Resource(BundleHandler, **ad)),
            
    url(r'^lobbyist_bundling/recipients\.(?P<emitter_format>.+)$',
        Resource(RecipientExplorerHandler, **ad)),
        
    url(r'^lobbyist_bundling/firms\.(?P<emitter_format>.+)$',
        Resource(FirmExplorerHandler, **ad)),
    
    url(r'^lobbyist_bundling/transactions\.(?P<emitter_format>.+)$',
        Resource(DetailExplorerHandler, **ad)),
    
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_summary\.(?P<emitter_format>.+)$',
        Resource(CandidateSummaryHandler, **ad)),
        
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_local_breakdown\.(?P<emitter_format>.+)$',
        Resource(CandidateStateHandler, **ad)),
        
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_timeline\.(?P<emitter_format>.+)$',
        Resource(CandidateTimelineHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_itemized\.(?P<emitter_format>.+)$',
        Resource(CandidateItemizedDownloadHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_indexp\.(?P<emitter_format>.+)$',
        Resource(CandidateIndExpHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/fec_indexp\.(?P<emitter_format>.+)$',
        Resource(CommitteeIndExpHandler, **ad)),
)



