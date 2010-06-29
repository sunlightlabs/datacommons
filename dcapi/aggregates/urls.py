
from dcapi.aggregates.contributions.handlers import OrgRecipientsHandler, \
    PolContributorsHandler, IndivOrgRecipientsHandler, IndivPolRecipientsHandler, \
    SectorsHandler, IndustriesBySectorHandler, PolLocalBreakdownHandler, \
    PolContributorTypeBreakdownHandler, OrgLevelBreakdownHandler, \
    OrgPartyBreakdownHandler, IndivPartyBreakdownHandler, SparklineHandler, \
    SparklineByPartyHandler, \
    TopPoliticiansByReceiptsHandler, TopIndividualsByContributionsHandler, \
    TopOrganizationsByContributionsHandler, ContributionAmountHandler
from dcapi.aggregates.lobbying.handlers import OrgRegistrantsHandler, \
    OrgIssuesHandler, OrgLobbyistsHandler, IndivRegistrantsHandler, \
    IndivIssuesHandler, IndivClientsHandler, RegistrantIssuesHandler, \
    RegistrantClientsHandler, RegistrantLobbyistsHandler
from django.conf.urls.defaults import patterns, url
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource

# We are using the default JSONEmitter so no need to explicitly
# register it. However, unregister those we don't need.
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }


urlpatterns = patterns('',

    url(r'^(pol|org|indiv)/(?P<entity_id>[a-f0-9]+)/sparkline_by_party.(?P<emitter_format>.+)$',
        Resource(SparklineByPartyHandler, **ad)),

    url(r'^(pol|org|indiv)/(?P<entity_id>[a-f0-9]+)/sparkline.(?P<emitter_format>.+)$',
        Resource(SparklineHandler, **ad)),

    # amount contributed by one entity to another
    url(r'^recipient/(?P<recipient_entity>[a-f0-9]+)/contributor/(?P<contributor_entity>[a-f0-9]+)/amount.(?P<emitter_format>.+)$',
        Resource(ContributionAmountHandler, **ad)),

    # contributors to a single politician
    url(r'^pol/(?P<entity_id>[a-f0-9]+)/contributors\.(?P<emitter_format>.+)$',
        Resource(PolContributorsHandler, **ad)),

    # contributions to a single politician, broken down by industry
    url(r'^pol/(?P<entity_id>[a-f0-9]+)/contributors/sectors\.(?P<emitter_format>.+)$',
        Resource(SectorsHandler, **ad)),

    # contributions to a single politician, broken down by industry sector
    url(r'^pol/(?P<entity_id>[a-f0-9]+)/contributors/sector/(?P<sector>.+)/industries\.(?P<emitter_format>.+)$',
        Resource(IndustriesBySectorHandler, **ad)),

    # contributions to a single politician, broken down to show percentages
    url(r'^pol/(?P<entity_id>[a-f0-9]+)/contributors/local_breakdown\.(?P<emitter_format>.+)$',
        Resource(PolLocalBreakdownHandler, **ad)),

    url(r'^pol/(?P<entity_id>[a-f0-9]+)/contributors/type_breakdown\.(?P<emitter_format>.+)$',
        Resource(PolContributorTypeBreakdownHandler, **ad)),

    # top N politicians by receipts for a cycle
    url(r'^pols/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopPoliticiansByReceiptsHandler, **ad)),

#    url(r'^pol/(?P<entity_id>[a-f0-9]+)/indiv_contributor/(?P<contrib_id>[a-f0-9]+).(?P<emitter_format>.+)$',
#        Resource(PolIndivContributorHandler, **ad)),
#
#    url(r'^pol/(?P<entity_id>[a-f0-9]+)/org_contributor/(?P<contrib_id>[a-f0-9]+).(?P<emitter_format>.+)$',
#        Resource(PolOrgContributorHandler, **ad)),

    # recipients from a single individual, broken down to show percentages
    url(r'^indiv/(?P<entity_id>[a-f0-9]+)/recipients/party_breakdown\.(?P<emitter_format>.+)$',
        Resource(IndivPartyBreakdownHandler, **ad)),

    # recipients from a single individual
    url(r'^indiv/(?P<entity_id>[a-f0-9]+)/recipient_orgs\.(?P<emitter_format>.+)$',
        Resource(IndivOrgRecipientsHandler, **ad)),

    url(r'^indiv/(?P<entity_id>[a-f0-9]+)/recipient_pols\.(?P<emitter_format>.+)$',
        Resource(IndivPolRecipientsHandler, **ad)),

    # lobbying - registrants this individual lobbied (worked) for
    url(r'indiv/(?P<entity_id>[a-f0-9]+)/registrants\.(?P<emitter_format>.+)$',
        Resource(IndivRegistrantsHandler, **ad)),

    # issues an individual lobbied on
    url(r'indiv/(?P<entity_id>[a-f0-9]+)/issues\.(?P<emitter_format>.+)$',
        Resource(IndivIssuesHandler, **ad)),

    # clients of the firms this individual lobbied with
    url(r'indiv/(?P<entity_id>[a-f0-9]+)/clients\.(?P<emitter_format>.+)$',
        Resource(IndivClientsHandler, **ad)),

    # top N individuals by contributions for a cycle
    url(r'^indivs/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopIndividualsByContributionsHandler, **ad)),

    # recipients from a single org//pac
    url(r'^org/(?P<entity_id>[a-f0-9]+)/recipients\.(?P<emitter_format>.+)$',
        Resource(OrgRecipientsHandler, **ad)),

    # recipients from a single org, broken down to show percentages
    url(r'^org/(?P<entity_id>[a-f0-9]+)/recipients/party_breakdown\.(?P<emitter_format>.+)$',
        Resource(OrgPartyBreakdownHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]+)/recipients/level_breakdown\.(?P<emitter_format>.+)$',
        Resource(OrgLevelBreakdownHandler, **ad)),

    url(r'^org/(?P<entity_id>[a-f0-9]+)/registrants\.(?P<emitter_format>.+)$',
        Resource(OrgRegistrantsHandler, **ad)),

    # issues an org hired people to
    url(r'^org/(?P<entity_id>[a-f0-9]+)/issues\.(?P<emitter_format>.+)',
        Resource(OrgIssuesHandler, **ad)),

    # lobbyists who worked with this org.
    url(r'org/(?P<entity_id>[a-f0-9]+)/lobbyists\.(?P<emitter_format>.+)',
        Resource(OrgLobbyistsHandler, **ad)),

    url(r'org/(?P<entity_id>[a-f0-9]+)/registrant/issues\.(?P<emitter_format>.+)',
        Resource(RegistrantIssuesHandler, **ad)),

    url(r'org/(?P<entity_id>[a-f0-9]+)/registrant/clients\.(?P<emitter_format>.+)',
        Resource(RegistrantClientsHandler, **ad)),

    url(r'org/(?P<entity_id>[a-f0-9]+)/registrant/lobbyists\.(?P<emitter_format>.+)',
        Resource(RegistrantLobbyistsHandler, **ad)),

    # top N organizations by contributions for a cycle
    url(r'^orgs/top_(?P<limit>[0-9]+)\.(?P<emitter_format>.+)$',
        Resource(TopOrganizationsByContributionsHandler, **ad)),

)



