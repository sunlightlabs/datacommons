from dcentity.models import *
from dcentity.admin import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

def merge(request):
    return render_to_response(
        "admin/change_list.html",
        {'entity_list' : Entity.objects.latest('timestamp')},
        RequestContext(request, {}),
    )