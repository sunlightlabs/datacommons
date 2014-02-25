from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponsePermanentRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from dcdata import contracts
from dcapi.common.handlers import RESERVED_PARAMS
import json

from locksmith.auth.models import ApiKey

API_KEY = getattr(settings, 'SYSTEM_API_KEY', None)
if not API_KEY:
    raise ImproperlyConfigured("SYSTEM_API_KEY is a required parameter")

#
# lookups documentation
#

def lookup(self, dataset, field):
    if dataset == 'contracts':
        attr = field.upper()
        if hasattr(contracts, attr):
            return render_to_response('docs/lookup.html', {
                'attr': attr,
                'lookup': getattr(contracts, attr),
            })
    raise Http404()


def search_count(request, search_resource):
    params = request.GET.copy()
    
    callback = params.get('callback', None)
    for param in RESERVED_PARAMS:
        params.pop(param, None)
    
    c = search_resource.handler.queryset(params).order_by().count()
    if callback:
        return HttpResponse("%s(%i)" % (callback, c), content_type='text/javascript')
    else:
        return HttpResponse("%i" % c, content_type='application/json')
    
    
def search_preview(request, search_resource):
    request.GET = request.GET.copy()
    request.GET['per_page'] = 30
    request.apikey = ApiKey.objects.get(key=API_KEY, status='A')
    return search_resource(request)

    
def search_download(request, search_resource):
    request.GET = request.GET.copy()
    request.apikey = ApiKey.objects.get(key=API_KEY, status='A')
    request.GET['per_page'] = 1000000
    request.GET['format'] = 'xls'
    response = search_resource(request)
    response['Content-Disposition'] = "attachment; filename=%s.xls" % search_resource.handler.filename
    response['Content-Type'] = "application/vnd.ms-excel; charset=utf-8"
    return response

