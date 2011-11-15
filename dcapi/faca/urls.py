from dcapi.common.views import no_format
from dcapi.faca.handlers import FACAFilterHandler
from django.conf.urls.defaults import patterns, url
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.resource import Resource


facafilter_handler = Resource(FACAFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', facafilter_handler, name='api_faca_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
