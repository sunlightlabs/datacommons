from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from locksmith.auth.authentication import PistonKeyAuthentication
from dcapi.aggregates.handlers import (TopContributorsHandler, TopRecipientsHandler, 
                                       ContributionsBreakdownHandler, RecipientsBreakdownHandler, 
                                       MetadataHandler, DetailHandler, TimelineHandler,
                                       IndustriesHandler, IndustriesBySectorHandler)

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
detail_handler = Resource(DetailHandler, **ad)
timeline_handler = Resource(TimelineHandler, **ad)
industries_handler = Resource(IndustriesHandler, **ad)
industries_sector_handler = Resource(IndustriesBySectorHandler, **ad)

urlpatterns = patterns('',
    # contributor breakdowns 
    # eg. /aggregates/entity/<entity_id>/contributors/breakdown.json?category=<category>
    url(r'^entity/(?P<entity_id>.+)/contributors/breakdown\.(?P<emitter_format>.+)$', 
        contributors_breakdown_handler, name='contributorsbreakdown_handler'),

    # recipient breakdowns 
    url(r'^entity/(?P<entity_id>.+)/recipients/breakdown\.(?P<emitter_format>.+)$', 
        recipients_breakdown_handler, name='recipientsbreakdown_handler'),

    # Top contributors TO an entity 
    # eg. /aggregates/entity/<entity_id>/contributors.json
    # optional parameters (with default values): cycle=2010&limit=10&type=pac,individual,
    url(r'^entity/(?P<entity_id>.+)/contributors\.(?P<emitter_format>.+)$', 
        topcontributors_handler, name='api_topcontributors_handler'),

    # Top recipients FROM an entity 
    # eg. /aggregates/entity/<entity_id>/recipients.json
    # optional parameters (with default values): cycle=2010&limit=10&type=pac,politician,
    url(r'^entity/(?P<entity_id>.+)/recipients\.(?P<emitter_format>.+)$', 
        toprecipients_handler, name='api_toprecipients_handler'),

    # entity metadata
    # eg. /aggregates/entity/<entity_id>/metadata.json?field=<specific field>
    url(r'^entity/(?P<entity_id>.+)/metadata\.(?P<emitter_format>.+)$', 
        metadata_handler, name='metadata_handler'),

    # detail
    # eg. /aggregates/entity/<entity_id>/detail.json?category=<type>&count=<n>
    url(r'^entity/(?P<entity_id>.+)/detail\.(?P<emitter_format>.+)$', 
        detail_handler, name='detail_handler'),

    # timeline                       
    # eg. /aggregates/entity/<entity_id>/timeline.json?start=<date>&end=<date>
    url(r'^entity/(?P<entity_id>.+)/timeline\.(?P<emitter_format>.+)$', 
        timeline_handler, name='timeline_handler'),

    # Top Industry Contributors to a candidate
    # eg. /aggregates/entity/<entity_id>/contributors/industries.json
    # optional parameters (with default values): cycle=2010&limit=10
    url(r'^entity/(?P<entity_id>.+)/contributors/industries\.(?P<emitter_format>.+)$', 
        industries_handler, name='industries_handler'),

    # Top Industry Contributors to a candidate, broken down by sector
    # eg. /aggregates/entity/<entity_id>/contributors/industry/<industry_id>/sectors.json
    # optional parameters (with default values): cycle=2010&limit=10
    url(r'^entity/(?P<entity_id>.+)/contributors/industry/(?P<industry_id>.+)/sectors\.(?P<emitter_format>.+)$', 
        industries_sector_handler, name='industries_sector_handler'),

)
