from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^/search/$', 'dcentity.custom_admin.views.search'),
    (r'^/(?P<merge_to>\w+)/(?P<merge_from>.*)', 'dcentity.custom_admin.views.merge')
)