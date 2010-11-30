from django.conf.urls.defaults import *
from handlers import EntityHandler, EntitySearchHandler, EntityAttributeHandler, EntitySimpleHandler, CurrentRaceHandler, \
        CurrentRaceDistrictsHandler
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
entityfilter_handler = Resource(EntitySearchHandler, **ad)
entity_attribute_handler = Resource(EntityAttributeHandler, **ad)
entitysimple_handler = Resource(EntitySimpleHandler, **ad)
current_race_handler = Resource(CurrentRaceHandler, **ad)
current_race_districts_handler = Resource(CurrentRaceDistrictsHandler, **ad)

urlpatterns = patterns('',
    url(r'^/race/districts\.(?P<emitter_format>.+)$', current_race_districts_handler, name='api_districts_current_race'),
    url(r'^/race/(?P<district>.+)\.(?P<emitter_format>.+)$', current_race_handler, name='api_entities_current_race'),
    url(r'^/id_lookup.json$', entity_attribute_handler, name='api_entity_attribute'),
    url(r'^/(?P<entity_id>[a-f0-9-]{32,36})\.(?P<emitter_format>.+)$', entity_handler, name='api_entities'),
    url(r'^/list.(?P<emitter_format>.+)$', entitysimple_handler, name='api_entities_simple'),
    url(r'^\.(?P<emitter_format>.+)$', entityfilter_handler, name='api_entities_filter'),
)
