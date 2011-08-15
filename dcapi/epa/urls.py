from dcapi.common.views import no_format
from dcapi.epa.handlers import EPAFilterHandler
from django.conf.urls.defaults import patterns, url
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.resource import Resource


epafilter_handler = Resource(EPAFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', epafilter_handler, name='api_earmarks_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)