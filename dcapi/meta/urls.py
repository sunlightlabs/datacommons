from django.conf.urls.defaults import *
from dcapi.contributions import CONTRIBUTION_SCHEMA
from dcapi.lobbying import LOBBYING_SCHEMA
from django.http import HttpResponse
from django.utils import simplejson as json

RESERVED_PARAMS = ('apikey','callback','limit','format','page','per_page','return_entities')

def methods(request):
    methods = {
        "http://transparencydata.com/api/1.0/": {
            "contributions.json": {
                "params": CONTRIBUTION_SCHEMA.get_field_names(),
                "required": [],
            },
            "lobbying.json": {
                "params": LOBBYING_SCHEMA.get_field_names(),
                "required": [],
            },
        }
    }
    resp = json.dumps(methods)
    return HttpResponse(resp, content_type='application/json')

urlpatterns = patterns('',
    url(r'^methods\.json$', methods, name='api_meta_methods'),
)
