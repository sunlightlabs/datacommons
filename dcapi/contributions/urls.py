from django.conf.urls.defaults import url, patterns
from piston.resource import Resource
from dcapi.contributions.handlers import ContributionFilterHandler,\
    ContributorGeoHandler
from dcapi.common.views import no_format
from locksmith.auth.authentication import PistonKeyAuthentication
from dcapi.contributions.bundling.handlers import BundlingFilterHandler

ad = { 'authentication': PistonKeyAuthentication() }
contributionfilter_handler = Resource(ContributionFilterHandler, **ad)
contributor_geo_handler = Resource(ContributorGeoHandler, **ad)
bundlingfilter_handler = Resource(BundlingFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^.(?P<emitter_format>csv|json|xls)$', contributionfilter_handler, name='api_contributions_filter'),
    url(r'^/contributor_geo.json', contributor_geo_handler),
    url(r'^.(?P<emitter_format>.*)$', no_format),
    url(r'^/bundled/.(?P<emitter_format>csv|json|xls)$', bundlingfilter_handler, name='api_contributions_filter'),
    url(r'^/bundled/.(?P<emitter_format>.*)$', no_format),
)
