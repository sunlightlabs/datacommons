from dcapi.common.views import no_format
from dcapi.earmarks.handlers import EarmarkFilterHandler
from django.conf.urls.defaults import patterns, url
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.resource import Resource


earmarkfilter_handler = Resource(EarmarkFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', earmarkfilter_handler, name='api_contracts_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)