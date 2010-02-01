from django.conf.urls.defaults import *

urlpatterns = patterns('django.contrib.auth.views',
    url(r'^auth/login/$', 'login', name="login"),
    url(r'^auth/logout/$', 'logout_then_login', name="logout"),
)

urlpatterns += patterns('matchbox.views_merge',
    url(r'^merge/merge/$', 'merge', name='matchbox_merge'),
    url(r'^merge/search/google/$', 'google_search', name='matchbox_google_search'),
    url(r'^merge/search/$', 'search', name='matchbox_search'),
    url(r'^merge/queue/(?P<queue_id>\d+)/$', 'queue', name='matchbox_queue'),
    url(r'^merge/debug/search/$', 'debug_search', name='matchbox_debug_search'),
    url(r'^merge/$', 'dashboard', name='matchbox_dashboard'),
)

urlpatterns += patterns('',
    url(r'^entity/(?P<entity_id>\w+)/associate/(?P<model_name>\w+)/$', 'matchbox.views.entity_associate', name='matchbox_entity_associate'),
    url(r'^entity/(?P<entity_id>\w+)/transactions/$', 'matchbox.views.entity_transactions', name='matchbox_entity_transactions'),
    url(r'^entity/(?P<entity_id>\w+)/notes/$', 'matchbox.views.entity_notes', name='matchbox_entity_notes'),
    url(r'^entity/(?P<entity_id>\w+)/$', 'matchbox.views.entity_detail', name='matchbox_entity'),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/merge/', 'permanent': False}),
)