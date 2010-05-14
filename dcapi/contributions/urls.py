from django.conf.urls.defaults import *
from piston.resource import Resource
from dcapi.contributions.handlers import ContributionFilterHandler
from dcapi.common.views import no_format
from locksmith.auth.authentication import PistonKeyAuthentication

ad = { 'authentication': PistonKeyAuthentication() }
contributionfilter_handler = Resource(ContributionFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>csv|json|xls)$', contributionfilter_handler, name='api_contributions_filter'),
    url(r'^.(?P<emitter_format>.*)$', no_format),
)
