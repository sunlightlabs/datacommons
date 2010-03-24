from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from dcapi.handlers import ContributionFilterHandler, EntityHandler, EntityFilterHandler
from dcapi.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter
from locksmith.auth.authentication import PistonKeyAuthentication

# streamingloggingemitters need to be rewritten but for now we'll just
# use the base included json emitter
# Emitter.register('json', StreamingLoggingJSONEmitter, 'application/json')

Emitter.register('csv', StreamingLoggingCSVEmitter, 'text/csv')
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }

contributionfilter_handler = Resource(ContributionFilterHandler, **ad)
entity_handler = Resource(EntityHandler, **ad)
entityfilter_handler = Resource(EntityFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^contributions.(?P<emitter_format>.+)$', contributionfilter_handler, name='api_contributions_filter'),

    url(r'^entities/(?P<entity_id>\w+).(?P<emitter_format>.+)$', entity_handler, name='api_entities'),
    url(r'^entities.(?P<emitter_format>.+)$', entityfilter_handler, name='api_entities_filter'),

    # each data set has its own area of the API and has its own
    # namespace. 'entities' is a core/common element to all APIs, and
    # aggregates has also been de-coupled from the contributions API. 
    url(r'^entities/', include('dcapi.entities.urls')), 
    url(r'^contributions/', include('dcapi.contributions.urls')), 
    url(r'^aggregates/', include('dcapi.aggregates.urls')), 

)

