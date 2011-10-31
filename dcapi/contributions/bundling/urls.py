from django.conf.urls.defaults import url, patterns
from piston.resource import Resource
from locksmith.auth.authentication import PistonKeyAuthentication
from dcapi.contributions.bundling.handlers import BundlingFilterHandler
from dcapi.common.views import no_format

ad = { 'authentication': PistonKeyAuthentication() }

bundlingfilter_handler = Resource(BundlingFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>csv|json|xls)$', bundlingfilter_handler, name='api_contributions_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
