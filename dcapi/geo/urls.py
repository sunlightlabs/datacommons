from django.conf.urls.defaults import patterns, url

from locksmith.auth.authentication import PistonKeyAuthentication
from piston.resource import Resource

from dcapi.geo.handlers import ZipcodeBoundingBoxHandler

ad = { 'authentication': PistonKeyAuthentication() }


urlpatterns = patterns('',

    # amount contributed by one entity to another
    url(r'^boundingbox/(?P<zipcode>[0-9]{5})$',
        Resource(ZipcodeBoundingBoxHandler, **ad))
)
