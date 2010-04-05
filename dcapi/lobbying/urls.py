from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from dcapi.lobbying.handlers import LobbyingFilterHandler
from dcapi.common.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter
from locksmith.auth.authentication import PistonKeyAuthentication

# Emitter.register('json', StreamingLoggingJSONEmitter, 'application/json')
# Emitter.register('csv', StreamingLoggingCSVEmitter, 'text/csv')
# Emitter.unregister('django')
# Emitter.unregister('pickle')
# Emitter.unregister('xml')
# Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }

lobbyingfilter_handler = Resource(LobbyingFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json)$', lobbyingfilter_handler, name='api_lobbying_filter'),
)
