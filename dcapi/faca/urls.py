from dcapi.common.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter, ExcelEmitter
from dcapi.common.views import no_format
from dcapi.faca.handlers import FACAFilterHandler
from django.conf.urls.defaults import patterns, url
from locksmith.auth.authentication import PistonKeyAuthentication
from piston.emitters import Emitter
from piston.resource import Resource


Emitter.register('json', StreamingLoggingJSONEmitter, 'application/json; charset=utf-8')
Emitter.register('csv', StreamingLoggingCSVEmitter, 'text/csv; charset=utf-8')
Emitter.register('xls', ExcelEmitter, 'application/vnd.ms-excel; charset=utf-8')

facafilter_handler = Resource(FACAFilterHandler,
                                authentication=PistonKeyAuthentication())

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>json|xls|csv)$', facafilter_handler, name='api_faca_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
