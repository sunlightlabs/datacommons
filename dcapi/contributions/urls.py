from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from dcapi.contributions.handlers import ContributionFilterHandler
from dcapi.common.emitters import StreamingLoggingCSVEmitter, StreamingLoggingJSONEmitter
from locksmith.auth.authentication import PistonKeyAuthentication


Emitter.register('json', StreamingLoggingJSONEmitter, 'application/json')
Emitter.register('csv', StreamingLoggingCSVEmitter, 'text/csv')
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }

contributionfilter_handler = Resource(ContributionFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>csv|json)$', contributionfilter_handler, name='api_contributions_filter'),
)
