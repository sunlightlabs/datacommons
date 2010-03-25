from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^auth/login/$', 'login', name="login"),
    url(r'^auth/logout/$', 'logout_then_login', name="logout"),
)

urlpatterns += patterns('matchbox.views_merge',
    url(r'^merge/search/google/$', 'google_search', name='matchbox_google_search'),
    url(r'^merge/search/$', 'search', name='matchbox_search'),
    url(r'^merge/queue/(?P<queue_id>\d+)/$', 'queue', name='matchbox_queue'),
    url(r'^merge/debug/search/$', 'debug_search', name='matchbox_debug_search'),
    url(r'^merge/$', 'merge', name='matchbox_merge'),
)

urlpatterns += patterns('',
    url(r'^entity/(?P<entity_id>\w+)/associate/(?P<model_name>\w+)/$', 'matchbox.views.entity_associate', name='matchbox_entity_associate'),
    url(r'^entity/(?P<entity_id>\w+)/transactions/$', 'matchbox.views.entity_transactions', name='matchbox_entity_transactions'),
    url(r'^entity/(?P<entity_id>\w+)/notes/$', 'matchbox.views.entity_notes', name='matchbox_entity_notes'),
    url(r'^entity/(?P<entity_id>\w+)/$', 'matchbox.views.entity_detail', name='matchbox_entity'),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/merge/', 'permanent': False}),
)

if (settings.DEBUG):  
    urlpatterns += patterns('',  
        url(r'^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'), 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  
    )  
