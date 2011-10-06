from django.conf.urls.defaults import url, patterns
from piston.resource import Resource
from locksmith.auth.authentication import PistonKeyAuthentication
from dcapi.contributions.bundling.handlers import BundlingFilterHandler
ad = { 'authentication': PistonKeyAuthentication() }

bundlingfilter_handler = Resource(BundlingFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>csv|json|xls)$', bundlingfilter_handler, name='api_contributions_filter'),
)
