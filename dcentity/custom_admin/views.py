from dcentity.models import *
from dcentity.admin import *
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from influenceexplorer import InfluenceExplorer
from dcentity import entity
import json

def merge(request, merge_to, merge_from):
    if request.method == 'GET':
        entities = Entity.objects.all()
        p = Paginator(entities, 25)
        result = p.page(1)
        try:
            merge_to = entities.filter(id=merge_to)[0]
        except:
            merge_to = None
        merge_from = entities.filter(id__in=merge_from.split('/'))
        
        return render_to_response(
            "admin/merge.html",
            {'entity_list' : result.object_list, 'merge_from': merge_from, 'merge_to': merge_to},
            RequestContext(request, {}),
        )
    elif request.method == 'POST':
        pass

def search(request):
    ie = InfluenceExplorer(settings.API_KEY)
    search = ie.entities.search(request.GET['q'])
    template_vars =  {
        'results' : Entity.objects.filter(id__in = [ x['id'] for x in search ] ).exclude(id=request.GET['not'])
    }
    return HttpResponse( render_to_string("admin/search_result.html", template_vars), mimetype="text/html")