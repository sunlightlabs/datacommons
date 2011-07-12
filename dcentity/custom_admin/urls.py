from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^/$', 'dcentity.custom_admin.views.merge'),
    (r'^/(?P<merge_to>\w+)$', 'dcentity.custom_admin.views.merge'),
)