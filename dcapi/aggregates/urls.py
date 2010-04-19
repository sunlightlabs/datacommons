from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from locksmith.auth.authentication import PistonKeyAuthentication
from dcapi.aggregates.handlers import (TopContributorsHandler, 
                                       TopRecipientsHandler, 
                                       ContributionsBreakdownHandler, 
                                       RecipientsBreakdownHandler, 
                                       MetadataHandler, 
#                                       DetailHandler, 
#                                       TimelineHandler,

                                       # new handlers
                                       OrgRecipientsHandler,
                                       OrgContributorsHandler,
                                       PolContributorsHandler,
                                       IndivRecipientsHandler,
                                       SectorsHandler,
                                       IndustriesBySectorHandler,
                                       OrgRecipientsBreakdownHandler,
                                       IndivRecipientsBreakdownHandler,
                                       PolContributorsBreakdownHandler,
                                       )

# We are using the default JSONEmitter so no need to explicitly
# register it. However, unregister those we don't need. 
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }

topcontributors_handler = Resource(TopContributorsHandler, **ad)
toprecipients_handler = Resource(TopRecipientsHandler, **ad)
contributors_breakdown_handler = Resource(ContributionsBreakdownHandler, **ad)
recipients_breakdown_handler = Resource(RecipientsBreakdownHandler, **ad)
metadata_handler = Resource(MetadataHandler, **ad)
#detail_handler = Resource(DetailHandler, **ad)
#timeline_handler = Resource(TimelineHandler, **ad)

# new api calls
org_recipients_handler = Resource(OrgRecipientsHandler, **ad)
org_contributors_handler = Resource(OrgContributorsHandler, **ad)
pol_contributors_handler = Resource(PolContributorsHandler, **ad)
indiv_recipients_handler = Resource(IndivRecipientsHandler, **ad)
sectors_handler = Resource(SectorsHandler, **ad)
industries_by_sector_handler = Resource(IndustriesBySectorHandler, **ad)
org_recipients_breakdown_handler = Resource(OrgRecipientsBreakdownHandler, **ad)
indiv_recipients_breakdown_handler = Resource(IndivRecipientsBreakdownHandler, **ad)
pol_contributors_breakdown_handler = Resource(PolContributorsBreakdownHandler, **ad)


urlpatterns = patterns('',
    # Top contributors TO an entity 
    # eg. /aggregates/entity/<entity_id>/contributors.json
    # optional parameters (with default values): cycle=2010&limit=10&type=pac,individual,
#    url(r'^entity/(?P<entity_id>.+)/contributors\.(?P<emitter_format>.+)$', 
#        topcontributors_handler, name='api_topcontributors_handler'),

    # Top recipients FROM an entity 
    # eg. /aggregates/entity/<entity_id>/recipients.json
    # optional parameters (with default values): cycle=2010&limit=10&type=pac,politician,
#    url(r'^entity/(?P<entity_id>.+)/recipients\.(?P<emitter_format>.+)$', 
#        toprecipients_handler, name='api_toprecipients_handler'),


    # new URLs

    # contributors to a single org/pac                       
    url(r'^org/(?P<entity_id>.+)/contributors.(?P<emitter_format>.+)$', 
        org_contributors_handler, name='org_contributors_handler'),

    # contributors to a single politician 
    url(r'^pol/(?P<entity_id>.+)/contributors\.(?P<emitter_format>.+)$', 
        pol_contributors_handler, name='pol_contributors_handler'),

    # recipients from a single org//pac 
    url(r'^org/(?P<entity_id>.+)/recipients\.(?P<emitter_format>.+)$', 
        org_recipients_handler, name='org_recipients_handler'),

    # recipients from a single individual
    url(r'^indiv/(?P<entity_id>.+)/recipients\.(?P<emitter_format>.+)$', 
        indiv_recipients_handler, name='indiv_recipients_handler'),

    # contributions to a single politician, broken down by industry
    url(r'^pol/(?P<entity_id>.+)/contributors/sectors\.(?P<emitter_format>.+)$', 
        sectors_handler, name='sectors_handler'),

    # contributions to a single politician, broken down by industry sector
    url(r'^pol/(?P<entity_id>.+)/contributors/sector/(?P<sector_id>.+)/industries\.(?P<emitter_format>.+)$', 
        industries_by_sector_handler, name='industries_by_sector_handler'),
    
    # recipients from a single individual, broken down to show percentages
    url(r'^indiv/(?P<entity_id>.+)/recipients/breakdown\.(?P<emitter_format>.+)$', 
        indiv_recipients_breakdown_handler, name='indiv_recipients_breakdown_handler'),

    # recipients from a single org, broken down to show percentages
    url(r'^org/(?P<entity_id>.+)/recipients/breakdown\.(?P<emitter_format>.+)$', 
        org_recipients_breakdown_handler, name='org_recipients_breakdown_handler'),

    # contributions to a single politician, broken down to show percentages
    url(r'^pol/(?P<entity_id>.+)/contributors/breakdown\.(?P<emitter_format>.+)$', 
        pol_contributors_breakdown_handler, name='pol_contributors_breakdown_handler'),


    # timeline                       
    # eg. /aggregates/entity/<entity_id>/timeline.json?start=<date>&end=<date>
#    url(r'^entity/(?P<entity_id>.+)/timeline\.(?P<emitter_format>.+)$', 
#        timeline_handler, name='timeline_handler'),


    # detail                        

)



