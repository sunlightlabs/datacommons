from django.conf.urls.defaults import *
from piston.emitters import Emitter
from piston.resource import Resource
from dcapi.aggregates.handlers import TopContributorsHandler, TopRecipientsHandler
from locksmith.auth.authentication import PistonKeyAuthentication

# We are using the default JSONEmitter so no need to explicitly
# register it. However, unregister those we don't need. 
Emitter.unregister('django')
Emitter.unregister('pickle')
Emitter.unregister('xml')
Emitter.unregister('yaml')

ad = { 'authentication': PistonKeyAuthentication() }

topcontributors_handler = Resource(TopContributorsHandler)#, **ad)
toprecipients_handler = Resource(TopRecipientsHandler)#, **ad)

urlpatterns = patterns('',
    # top contributors TO an entity
    url(r'^entity/(?P<entity_id>.+)/contributors\.(?P<emitter_format>.+)$', 
        topcontributors_handler, name='api_topcontributors_handler'),
    # top recipients FROM an entity
    url(r'^entity/(?P<entity_id>.+)/recipients\.(?P<emitter_format>.+)$', 
        toprecipients_handler, name='api_toprecipients_handler'),
)
