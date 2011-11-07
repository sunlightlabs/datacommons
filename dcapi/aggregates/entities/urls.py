from django.conf.urls.defaults import *
from handlers import EntityHandler, EntitySearchHandler, EntityAttributeHandler, EntitySimpleHandler
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource

Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }

entity_handler = Resource(EntityHandler, **ad)
entityfilter_handler = Resource(EntitySearchHandler, **ad)
entity_attribute_handler = Resource(EntityAttributeHandler, **ad)
entitysimple_handler = Resource(EntitySimpleHandler, **ad)

urlpatterns = patterns('',
    url(r'^/id_lookup.json$', entity_attribute_handler, name='api_entity_attribute'),
    url(r'^/(?P<entity_id>[a-f0-9-]{32,36})\.(?P<emitter_format>.+)$', entity_handler, name='api_entities'),
    url(r'^/list.(?P<emitter_format>.+)$', entitysimple_handler, name='api_entities_simple'),
    url(r'^\.(?P<emitter_format>.+)$', entityfilter_handler, name='api_entities_filter'),
)
