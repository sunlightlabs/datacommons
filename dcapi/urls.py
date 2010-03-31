from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # each data set has its own area of the API and has its own
    # namespace. 'entities' is a core/common element to all APIs, and
    # aggregates has also been de-coupled from the contributions API. 
    url(r'^entities', include('dcapi.entities.urls')), 
    url(r'^contributions', include('dcapi.contributions.urls')), 
    url(r'^lobbying', include('dcapi.lobbying.urls')),
    url(r'^aggregates/', include('dcapi.aggregates.urls')), 

)

