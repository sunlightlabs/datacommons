from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from locksmith.auth.authentication import PistonKeyAuthentication
from dcapi.aggregates.handlers import (TopContributorsHandler, TopRecipientsHandler, 
                                       ContributionsBreakdownHandler, RecipientsBreakdownHandler, 
                                       MetadataHandler, DetailHandler, TimelineHandler)

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


urlpatterns = patterns('',
    # contributor breakdowns 
    # eg. /aggregates/entity/<entity_id>/contributors/breakdown.json?category=<category>
    url(r'^entity/(?P<entity_id>.+)/contributors/breakdown\.(?P<emitter_format>.+)$', 
        contributors_breakdown_handler, name='contributorsbreakdown_handler'),

    # recipient breakdowns 
    url(r'^entity/(?P<entity_id>.+)/recipients/breakdown\.(?P<emitter_format>.+)$', 
        recipients_breakdown_handler, name='recipientsbreakdown_handler'),

    # top contributors TO an entity 
    url(r'^entity/(?P<entity_id>.+)/contributors\.(?P<emitter_format>.+)$', 
        topcontributors_handler, name='api_topcontributors_handler'),
    # top recipients FROM an entity 
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

)
