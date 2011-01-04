from dcapi.common.views import no_format
from dcapi.grants.handlers import GrantsFilterHandler
from django.conf.urls.defaults import *
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource

grantsfilter_handler = Resource(GrantsFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', grantsfilter_handler, name='api_grants_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
