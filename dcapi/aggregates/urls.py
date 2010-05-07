
from dcapi.aggregates.contributions.handlers import OrgRecipientsHandler, \
    PolContributorsHandler, IndivOrgRecipientsHandler, IndivPolRecipientsHandler, \
    SectorsHandler, IndustriesBySectorHandler, PolLocalBreakdownHandler, \
    PolContributorTypeBreakdownHandler, OrgLevelBreakdownHandler, \
    OrgPartyBreakdownHandler, IndivPartyBreakdownHandler
from dcapi.aggregates.lobbying.handlers import OrgRegistrantsHandler, \
    OrgIssuesHandler, OrgLobbyistsHandler
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


org_recipients_handler = Resource(OrgRecipientsHandler, **ad)
pol_contributors_handler = Resource(PolContributorsHandler, **ad)
indiv_org_recipients_handler = Resource(IndivOrgRecipientsHandler, **ad)
indiv_pol_recipients_handler = Resource(IndivPolRecipientsHandler, **ad)
sectors_handler = Resource(SectorsHandler, **ad)
industries_by_sector_handler = Resource(IndustriesBySectorHandler, **ad)
org_level_breakdown_handler = Resource(OrgLevelBreakdownHandler, **ad)
org_party_breakdown_handler = Resource(OrgPartyBreakdownHandler, **ad)
indiv_party_breakdown_handler = Resource(IndivPartyBreakdownHandler, **ad)
pol_local_breakdown_handler = Resource(PolLocalBreakdownHandler, **ad)
pol_type_breakdown_handler = Resource(PolContributorTypeBreakdownHandler, **ad)

lobbying_org_registrants_handler = Resource(OrgRegistrantsHandler, **ad)
lobbying_org_issues_handler = Resource(OrgIssuesHandler, **ad)
lobbying_org_lobbyists_handler = Resource(OrgLobbyistsHandler, **ad)


urlpatterns = patterns('',

    # contributors to a single politician 
    url(r'^pol/(?P<entity_id>.+)/contributors\.(?P<emitter_format>.+)$', 
        pol_contributors_handler),

    # contributions to a single politician, broken down by industry
    url(r'^pol/(?P<entity_id>.+)/contributors/sectors\.(?P<emitter_format>.+)$', 
        sectors_handler),

    # contributions to a single politician, broken down by industry sector
    url(r'^pol/(?P<entity_id>.+)/contributors/sector/(?P<sector>.+)/industries\.(?P<emitter_format>.+)$', 
        industries_by_sector_handler),

    # contributions to a single politician, broken down to show percentages
    url(r'^pol/(?P<entity_id>.+)/contributors/local_breakdown\.(?P<emitter_format>.+)$', 
        pol_local_breakdown_handler),
    
    url(r'^pol/(?P<entity_id>.+)/contributors/type_breakdown\.(?P<emitter_format>.+)$', 
        pol_type_breakdown_handler),
    
    # recipients from a single individual, broken down to show percentages
    url(r'^indiv/(?P<entity_id>.+)/recipients/party_breakdown\.(?P<emitter_format>.+)$', 
        indiv_party_breakdown_handler),

    # recipients from a single individual
    url(r'^indiv/(?P<entity_id>.+)/recipient_orgs\.(?P<emitter_format>.+)$', 
        indiv_org_recipients_handler),

    url(r'^indiv/(?P<entity_id>.+)/recipient_pols\.(?P<emitter_format>.+)$', 
        indiv_pol_recipients_handler),


    # recipients from a single org//pac 
    url(r'^org/(?P<entity_id>.+)/recipients\.(?P<emitter_format>.+)$', 
        org_recipients_handler),

    # recipients from a single org, broken down to show percentages
    url(r'^org/(?P<entity_id>.+)/recipients/party_breakdown\.(?P<emitter_format>.+)$', 
        org_party_breakdown_handler),

    url(r'^org/(?P<entity_id>.+)/recipients/level_breakdown\.(?P<emitter_format>.+)$', 
        org_level_breakdown_handler),

    url(r'^org/(?P<entity_id>.+)/registrants\.(?P<emitter_format>.+)$',
        lobbying_org_registrants_handler),
        
    url(r'^org/(?P<entity_id>.+)/issues\.(?P<emitter_format>.+)',
        lobbying_org_issues_handler),
        
    url(r'org/(?P<entity_id>.+)/lobbyists\.(?P<emitter_format>.+)',
        lobbying_org_lobbyists_handler),
)



