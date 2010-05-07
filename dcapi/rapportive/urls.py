from django.conf.urls.defaults import *
from piston.resource import Resource
from dcapi.rapportive.handlers import RapletHandler
from dcapi.common.views import no_format

raplet_handler = Resource(RapletHandler)

urlpatterns = patterns('',
    url(r'^rapportive.(?P<emitter_format>json)$', raplet_handler, name='raplet'),
    url(r'^rapportive(?P<emitter_format>.*)$', no_format),
)
