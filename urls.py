from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template, redirect_to

DATA_BASE_URL = getattr(settings, "DATA_BASE_URL", "http://data.influenceexplorer.com/")

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/1.0/', include('dcapi.urls')),
    url(r'^api/locksmith/', include('locksmith.auth.urls')),
    url(r'^data/', include('public.urls')),
    url(r'^(?P<old_url>.*)$', redirect_to, {'url': DATA_BASE_URL + '%(old_url)s', 'query_string': True}),
)

if (settings.DEBUG):  
    urlpatterns += patterns('',  
        url(r'^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'), 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  
    )
