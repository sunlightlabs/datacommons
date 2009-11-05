from django.conf.urls.defaults import *

urlpatterns = patterns('matchbox.views',
    url(r'^transactions', 'transactions_page'),
    url(r'^entities', 'entities_page'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^auth/login/$', 'login', name="login"),
    url(r'^auth/logout/$', 'logout_then_login', name="logout"),
)

urlpatterns += patterns('matchbox.views',
    url(r'^entity/(?P<entity_id>\w+)/$', 'entity_detail', name='matchbox_entity'),
    url(r'^merge/$', 'merge', name='matchbox_merge'),
    url(r'^search/google/$', 'google_search', name='matchbox_google_search'),
    url(r'^search/$', 'search', name='matchbox_search'),
    url(r'^queue/(?P<queue_id>\d+)/$', 'queue', name='matchbox_queue'),
    url(r'^$', 'dashboard', name='matchbox_dashboard'),
)