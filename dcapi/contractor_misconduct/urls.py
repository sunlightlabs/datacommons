from dcapi.common.views import no_format
from dcapi.contractor_misconduct.handlers import ContractorMisconductFilterHandler
from django.conf.urls.defaults import *
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.resource import Resource

from dcapi.common.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter, ExcelEmitter
from piston.emitters import Emitter

Emitter.register('json', StreamingLoggingJSONEmitter, 'application/json; charset=utf-8')
Emitter.register('csv', StreamingLoggingCSVEmitter, 'text/csv; charset=utf-8')
Emitter.register('xls', ExcelEmitter, 'application/vnd.ms-excel; charset=utf-8')

contractor_misconduct_filter_handler = Resource(ContractorMisconductFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', contractor_misconduct_filter_handler, name='api_contractor_misconduct_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)

