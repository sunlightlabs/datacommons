from dcapi.common.views import no_format
from dcapi.lobbying.emitters import LobbyingExcelEmitter
from dcapi.lobbying.handlers import LobbyingFilterHandler
from django.conf.urls.defaults import *
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource

class LobbyingResource(Resource):
    def determine_emitter(self, request, *args, **kwargs):
        em = super(LobbyingResource, self).determine_emitter(request, *args, **kwargs)
        return 'xls-lobbying' if em == 'xls' else em

Emitter.register('xls-lobbying', LobbyingExcelEmitter, 'application/vnd.ms-excel; charset=utf-8')

lobbyingfilter_handler = LobbyingResource(LobbyingFilterHandler,
                                          authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls)$', lobbyingfilter_handler, name='api_lobbying_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
