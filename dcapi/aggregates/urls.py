from dcapi.aggregates.contributions.handlers import OrgRecipientsHandler, \
    PolContributorsHandler, IndivOrgRecipientsHandler, IndivPolRecipientsHandler, \
    SectorsHandler, IndustriesHandler, UnknownIndustriesHandler, PolLocalBreakdownHandler, \
    PolContributorTypeBreakdownHandler, OrgLevelBreakdownHandler, \
    OrgPartyBreakdownHandler, IndivPartyBreakdownHandler, TopPoliticiansByReceiptsHandler,  \
    TopIndividualsByContributionsHandler, TopOrganizationsByContributionsHandler, \
    TopIndustriesByContributionsHandler, IndustryOrgHandler, \
    ContributionAmountHandler, OrgPACRecipientsHandler, \
    TopIndividualContributorsToPartyHandler, \
    TopIndividualContributorsByAreaHandler, \
    TopLobbyistBundlersHandler, TopPoliticiansByReceiptsByOfficeHandler, \
    TopIndustryContributorsToPartyHandler, \
    TopOrgContributorsByAreaContributorTypeHandler, \
    SubIndustryTotalsHandler, TopIndustriesTimeSeriesHandler, \
    OrgPartySummaryHandler, OrgStateFedSummaryHandler, OrgToPolGroupSummaryHandler, \
    ContributorPartySummaryHandler, ContributorStateFedSummaryHandler, \
    ContributorRecipientTypeSummaryHandler, \
    LobbyistPartySummaryHandler, LobbyistStateFedSummaryHandler, \
    LobbyistRecipientTypeSummaryHandler
from dcapi.aggregates.contributions.bundle_handlers import BundleHandler, \
    RecipientExplorerHandler, FirmExplorerHandler, DetailExplorerHandler
from dcapi.aggregates.lobbying.handlers import OrgRegistrantsHandler, \
    OrgIssuesHandler, OrgBillsHandler, OrgLobbyistsHandler, \
    IndivRegistrantsHandler, IndivIssuesHandler, IndivClientsHandler, \
    RegistrantIssuesHandler, RegistrantBillsHandler, RegistrantClientsHandler, \
    RegistrantLobbyistsHandler, TopFirmsByIncomeHandler, \
    TopOrgsLobbyingHandler, OrgIssuesSummaryHandler, OrgBillsSummaryHandler
from dcapi.aggregates.spending.handlers import OrgFedSpendingHandler
from dcapi.aggregates.earmarks.handlers import TopEarmarksHandler,\
    LocalEarmarksHandler
from dcapi.aggregates.pogo.handlers import TopContractorMisconductHandler
from dcapi.aggregates.epa.handlers import TopViolationActionsHandler
from dcapi.aggregates.regulations.handlers import RegulationsTextHandler, \
    RegulationsSubmitterHandler, RegulationsDocketTextHandler, \
    RegulationsDocketSubmitterHandler, TopRegsSubmittersHandler
from dcapi.aggregates.fec.handlers import CandidateSummaryHandler, \
    CommitteeSummaryHandler, CandidateStateHandler, \
    CandidateTimelineHandler, CandidateItemizedDownloadHandler, \
    CommitteeItemizedDownloadHandler, CommitteeTopContribsHandler, \
    ElectionSummaryHandler
from dcapi.aggregates.independentexpenditures.handlers import \
    CandidateIndExpHandler, CommitteeIndExpHandler, \
    CandidateIndExpDownloadHandler, CommitteeIndExpDownloadHandler, \
    TopPACsByIndExpsHandler, TopCandidatesAffectedByIndExpHandler

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

    #url(r'^org/(?P<entity_id>[a-f0-9]{32})/recipients/office_type_breakdown\.(?P<emitter_format>.+)$',

    #    Resource(OrgOfficeTypeBreakdownHandler, **ad)),

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

    # fec
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_summary\.(?P<emitter_format>.+)$',
        Resource(CandidateSummaryHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/fec_summary\.(?P<emitter_format>.+)$',
        Resource(CommitteeSummaryHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_local_breakdown\.(?P<emitter_format>.+)$',
        Resource(CandidateStateHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_timeline\.(?P<emitter_format>.+)$',
        Resource(CandidateTimelineHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_itemized\.(?P<emitter_format>.+)$',
        Resource(CandidateItemizedDownloadHandler, **ad)),

    # independent expenditures
    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_indexp\.(?P<emitter_format>.+)$',
        Resource(CandidateIndExpHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]{32})/fec_indexp_itemized\.(?P<emitter_format>.+)$',
        Resource(CandidateIndExpDownloadHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/fec_indexp\.(?P<emitter_format>.+)$',
        Resource(CommitteeIndExpHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/fec_top_contribs\.(?P<emitter_format>.+)$',
        Resource(CommitteeTopContribsHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/fec_itemized\.(?P<emitter_format>.+)$',
        Resource(CommitteeItemizedDownloadHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]{32})/fec_indexp_itemized\.(?P<emitter_format>.+)$',
        Resource(CommitteeIndExpDownloadHandler, **ad)),

    # -- entity type top lists --
    # ---------------------------
    # ------- individuals -------
    # top N individuals by contributions for a cycle
    url(r'^indivs/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopIndividualsByContributionsHandler, **ad)),

    # top N individuals by contributions to party for a cycle
    url(r'^indivs/party/(?P<party>[RD])/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopIndividualContributorsToPartyHandler, **ad)),

    # top lobbyists
    #url(r'^indivs/lobbyists/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
    #    Resource(TopLobbyistsHandler, **ad)),

    # top lobbyist bundlers
    url(r'^indivs/lobbyist_bundlers/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopLobbyistBundlersHandler, **ad)),

    # top indiv contributors at state or federal level
    url(r'^indivs/(?P<area>state|federal)/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopIndividualContributorsByAreaHandler, **ad)),

    # ------ organizations ------
    # top PACs by independent expenditures
    url(r'^orgs/indexp/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopPACsByIndExpsHandler, **ad)),

    # top lobbying firms by income
    url(r'^orgs/lobbying_firms/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopFirmsByIncomeHandler, **ad)),

    # top orgs by regulation submissions
    url(r'^orgs/regulations/submitters/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopRegsSubmittersHandler, **ad)),

    # top org contributors by pac/employee at state or federal level
    url(r'^orgs/(?P<area>state|federal)/(?P<pac_or_employee>pac|employee)/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopOrgContributorsByAreaContributorTypeHandler, **ad)),

    # --------- industries -------
    # top N industry donors to party
    url(r'^industries/party/(?P<party>[RD])/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopIndustryContributorsToPartyHandler, **ad)),

    # top lobbying clients by spending
    url(r'^(?P<entity_type>industries|orgs)/lobbying/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopOrgsLobbyingHandler, **ad)),

    url(r'^industries/subindustry_totals\.(?P<emitter_format>.+)$',
        Resource(SubIndustryTotalsHandler, **ad)),

    url(r'^industries/top_(?P<limit>[0-9]+)_industries_time_series\.(?P<emitter_format>.+)$',
        Resource(TopIndustriesTimeSeriesHandler, **ad)),

    # -------- politicians -------
    # top political fundraisers by office
    url(r'^pols/(?P<office>president|senate|house|governor)/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopPoliticiansByReceiptsByOfficeHandler, **ad)),

    # top candidates targeted by independent expenditures
    url(r'^pols/indexp/(?P<office>president|senate|house)/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopCandidatesAffectedByIndExpHandler, **ad)),

    # --------- election summary ----------
    url(r'^election/2012/summary\.(?P<emitter_format>.+)$',
        Resource(ElectionSummaryHandler, **ad)),

    #########################################################
    # ---------- Summaries for Entity Landing Pages --------
    # Separating these because the mappings are nav-specific and don't fit well
    # into the patterns above

    # ---------- GROUPS >> Organizations: Contributions -------------
    # summary of orgs to party
    url(r'^summary/org/party.(?P<emitter_format>.+)$',
        Resource(OrgPartySummaryHandler, **ad)),

    # summary of orgs to state/fed candidates
    url(r'^summary/org/state_fed.(?P<emitter_format>.+)$',
        Resource(OrgStateFedSummaryHandler, **ad)),

    # summary of orgs' group vs individual contributions
    url(r'^summary/org/pol_group.(?P<emitter_format>.+)$',
        Resource(OrgToPolGroupSummaryHandler, **ad)),

    #url(r'^summary/organization/office_type.(?P<emitter_format>.+)$',
    #    Resource(OrgOfficeTypeSummaryHandler, **ad)),

    # ----------- GROUPS >> Organizations: Lobbying -------------
    # TODO: top 10 lobbied issues for all orgs, each with top 10 orgs listed
    url(r'^summary/org/issues.(?P<emitter_format>.+)$',
        Resource(OrgIssuesSummaryHandler, **ad)),

    # TODO: top 10 lobbied issues for all orgs, each with top 10 orgs listed
    url(r'^summary/org/bills.(?P<emitter_format>.+)$',
        Resource(OrgBillsSummaryHandler, **ad)),

    # ----------- GROUPS >> Organizations: Regulations -------------
    # TODO: handler for top 10 commented dockets for all orgs, each with top 10 orgs listed

    # TODO: handler for top 10 orgs mentioned in dockets

    # ----------- GROUPS >> Organizations: Earmarks -------------
    # TODO: design summary stats for earmarks
    #url(r'^summary/organization/earmark.(?P<emitter_format>.+)$',
    #    Resource(OrgEarmarkSummaryHandler, **ad)),

    # ----------- GROUPS >> Organizations: Federal Spending --------------
    # TODO: design summary stats for federal spending

    # ----------- GROUPS >> Organizations: Contractor Misconduct ---------
    # TODO: design summary stats for contractor misconduct

    # ----------- GROUPS >> Organizations: EPA Violations ----------------
    # TODO: design summary stats for epa violations

    # ----------- GROUPS >> Organizations: Advisory Committees -----------
    # TODO: design summary stats for advisory committees (FACA)

    # ----------- PEOPLE >> Contributors: Contributions -----------
    # summary of contributors to party
    url(r'^summary/contributor/party.(?P<emitter_format>.+)$',
        Resource(ContributorPartySummaryHandler, **ad)),

    # summary of contributors to state/fed candidates
    url(r'^summary/contributor/state_fed.(?P<emitter_format>.+)$',
        Resource(ContributorStateFedSummaryHandler, **ad)),

    # summary of contributors to groups vs politicians
    url(r'^summary/contributor/recipient_type.(?P<emitter_format>.+)$',
        Resource(ContributorRecipientTypeSummaryHandler, **ad)),

    # ----------- PEOPLE >> Lobbyists: Contributions -----------
    # summary of lobbyists to party
    url(r'^summary/lobbyist/party.(?P<emitter_format>.+)$',
        Resource(LobbyistPartySummaryHandler, **ad)),

    # summary of lobbyists to state/fed candidates
    url(r'^summary/lobbyist/state_fed.(?P<emitter_format>.+)$',
        Resource(LobbyistStateFedSummaryHandler, **ad)),

    # summary of lobbyists to groups vs politicians
    url(r'^summary/lobbyist/recipient_type.(?P<emitter_format>.+)$',
        Resource(LobbyistRecipientTypeSummaryHandler, **ad)),

)
