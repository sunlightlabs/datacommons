from dcentity.models import *
from dcentity.admin import *
from dcentity.entity import merge_entities
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from dcentity import entity
from django import forms
import json
from django.conf import settings

@staff_member_required
def merge(request, merge_to = None):
    try:
        merge_to = Entity.objects.get(id=merge_to)
    except:
        merge_to = None
    if request.method == 'GET':    
        return render_to_response(
            "admin/merge.html",
            {'merge_to': merge_to, 'api_key': settings.API_KEY},
            RequestContext(request, {}),
        )
    elif request.method == 'POST':
        merge_from = Entity.objects.filter(id__in = request.POST.getlist('to_merge')).values_list('id')
        merge_entities(merge_from,request.POST["merge_to"])
        request.user.message_set.create(message=merge_from[0])
        return HttpResponseRedirect("/admin/dcentity/entity/"+request.POST["merge_to"])