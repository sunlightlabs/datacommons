from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from dcapi.lobbying.handlers import LobbyingFilterHandler
from dcapi.common.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter
from dcapi.common.views import no_format
from locksmith.auth.authentication import PistonKeyAuthentication

ad = { 'authentication': PistonKeyAuthentication() }

lobbyingfilter_handler = Resource(LobbyingFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json)$', lobbyingfilter_handler, name='api_lobbying_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
