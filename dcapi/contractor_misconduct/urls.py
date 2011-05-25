from dcapi.common.views import no_format
from dcapi.contractor_misconduct.handlers import ContractorMisconductFilterHandler
from django.conf.urls.defaults import *
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.resource import Resource

contractor_misconduct_filter_handler = Resource(ContractorMisconductFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', contractor_misconduct_filter_handler, name='api_contracts_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)

