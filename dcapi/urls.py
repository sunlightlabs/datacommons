from django.conf.urls.defaults import *
from dcapi.common.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter, ExcelEmitter
from piston.emitters import Emitter

Emitter.register('json', StreamingLoggingJSONEmitter, 'application/json; charset=utf-8')
Emitter.register('csv', StreamingLoggingCSVEmitter, 'text/csv; charset=utf-8')
Emitter.register('xls', ExcelEmitter, 'application/vnd.ms-excel; charset=utf-8')
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

urlpatterns = patterns('',
    # each data set has its own area of the API and has its own
    # namespace. 'entities' is a core/common element to all APIs, and
    # aggregates has also been de-coupled from the contributions API. 
    url(r'^entities', include('dcapi.aggregates.entities.urls')),
    url(r'^contracts', include('dcapi.contracts.urls')),
    url(r'^contributions', include('dcapi.contributions.urls')),
    url(r'^grants', include('dcapi.grants.urls')),
    url(r'^lobbying', include('dcapi.lobbying.urls')),
    url(r'^poligraft/', include('dcapi.pg_rapportive.urls')), 
    url(r'^earmarks', include('dcapi.earmarks.urls')),
    url(r'^aggregates/', include('dcapi.aggregates.urls')), 
    url(r'^', include('dcapi.rapportive.urls')),
)
