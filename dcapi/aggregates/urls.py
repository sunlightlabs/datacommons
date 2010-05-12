
from dcapi.aggregates.contributions.handlers import OrgRecipientsHandler, \
    PolContributorsHandler, IndivOrgRecipientsHandler, IndivPolRecipientsHandler, \
    SectorsHandler, IndustriesBySectorHandler, PolLocalBreakdownHandler, \
    PolContributorTypeBreakdownHandler, OrgLevelBreakdownHandler, \
    OrgPartyBreakdownHandler, IndivPartyBreakdownHandler
from dcapi.aggregates.lobbying.handlers import OrgRegistrantsHandler, \
    OrgIssuesHandler, OrgLobbyistsHandler, IndivRegistrantsHandler,\
    IndivIssuesHandler, IndivClientsHandler
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

    # contributors to a single politician 
    url(r'^pol/(?P<entity_id>.+)/contributors\.(?P<emitter_format>.+)$', 
        Resource(PolContributorsHandler, **ad)),

    # contributions to a single politician, broken down by industry
    url(r'^pol/(?P<entity_id>.+)/contributors/sectors\.(?P<emitter_format>.+)$', 
        Resource(SectorsHandler, **ad)),

    # contributions to a single politician, broken down by industry sector
    url(r'^pol/(?P<entity_id>.+)/contributors/sector/(?P<sector>.+)/industries\.(?P<emitter_format>.+)$', 
        Resource(IndustriesBySectorHandler, **ad)),

    # contributions to a single politician, broken down to show percentages
    url(r'^pol/(?P<entity_id>.+)/contributors/local_breakdown\.(?P<emitter_format>.+)$', 
        Resource(PolLocalBreakdownHandler, **ad)),
    
    url(r'^pol/(?P<entity_id>.+)/contributors/type_breakdown\.(?P<emitter_format>.+)$', 
        Resource(PolContributorTypeBreakdownHandler, **ad)),
    
    
    # recipients from a single individual, broken down to show percentages
    url(r'^indiv/(?P<entity_id>.+)/recipients/party_breakdown\.(?P<emitter_format>.+)$', 
        Resource(IndivPartyBreakdownHandler, **ad)),

    # recipients from a single individual
    url(r'^indiv/(?P<entity_id>.+)/recipient_orgs\.(?P<emitter_format>.+)$', 
        Resource(IndivOrgRecipientsHandler, **ad)),

    url(r'^indiv/(?P<entity_id>.+)/recipient_pols\.(?P<emitter_format>.+)$', 
        Resource(IndivPolRecipientsHandler, **ad)),

    # lobbying - registrants this individual lobbied (worked) for
    url(r'indiv/(?P<entity_id>.+)/registrants\.(?P<emitter_format>.+)$',
        Resource(IndivRegistrantsHandler, **ad)),

    # issues an individual lobbied on
    url(r'indiv/(?P<entity_id>.+)/issues\.(?P<emitter_format>.+)$',
        Resource(IndivIssuesHandler, **ad)),
        
    # clients of the firms this individual lobbied with
    url(r'indiv/(?P<entity_id>.+)/clients\.(?P<emitter_format>.+)$',
        Resource(IndivClientsHandler, **ad)),
                

    # recipients from a single org//pac 
    url(r'^org/(?P<entity_id>.+)/recipients\.(?P<emitter_format>.+)$', 
        Resource(OrgRecipientsHandler, **ad)),

    # recipients from a single org, broken down to show percentages
    url(r'^org/(?P<entity_id>.+)/recipients/party_breakdown\.(?P<emitter_format>.+)$', 
        Resource(OrgPartyBreakdownHandler, **ad)),

    url(r'^org/(?P<entity_id>.+)/recipients/level_breakdown\.(?P<emitter_format>.+)$', 
        Resource(OrgLevelBreakdownHandler, **ad)),

    url(r'^org/(?P<entity_id>.+)/registrants\.(?P<emitter_format>.+)$',
        Resource(OrgRegistrantsHandler, **ad)),
        
    # issues an org hired people to 
    url(r'^org/(?P<entity_id>.+)/issues\.(?P<emitter_format>.+)',
        Resource(OrgIssuesHandler, **ad)),
        
    # lobbyists who worked with this org.
    url(r'org/(?P<entity_id>.+)/lobbyists\.(?P<emitter_format>.+)',
        Resource(OrgLobbyistsHandler, **ad)),
)



