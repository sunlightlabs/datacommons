from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('matchbox.urls')),
)

if (settings.DEBUG):  
    urlpatterns += patterns('',  
        url(r'^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'), 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  
    )  
