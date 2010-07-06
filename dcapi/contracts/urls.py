from dcapi.common.views import no_format
from dcapi.contracts.handlers import ContractsFilterHandler
from django.conf.urls.defaults import *
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource

contractsfilter_handler = Resource(ContractsFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', contractsfilter_handler, name='api_contracts_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
