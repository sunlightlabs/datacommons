from dcapi.entities.handlers import EntityHandler, EntityFilterHandler, \
    EntityAttributeHandler, EntityTotalsHandler
from django.conf.urls.defaults import *
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource
#from dcapi.common.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter

# streamingloggingemitters need to be rewritten but for now we'll just
# use the base included json emitter
# Emitter.register('json', StreamingLoggingJSONEmitter, 'application/json')
# Emitter.register('csv', StreamingLoggingCSVEmitter, 'text/csv')
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }

entity_handler = Resource(EntityHandler, **ad)
entityfilter_handler = Resource(EntityFilterHandler, **ad)
entity_attribute_handler = Resource(EntityAttributeHandler, **ad)
entity_totals_handler = Resource(EntityTotalsHandler, **ad)

urlpatterns = patterns('',
    url(r'^/id_lookup$', entity_attribute_handler, name='api_entity_attribute'),
    url(r'^/(?P<entity_id>\w+)/totals.(?P<emitter_format>.+)$', entity_totals_handler, name='entity_totals_handler'),
    url(r'^/(?P<entity_id>\w+).(?P<emitter_format>.+)$', entity_handler, name='api_entities'),
    url(r'^.(?P<emitter_format>.+)$', entityfilter_handler, name='api_entities_filter'),
)
