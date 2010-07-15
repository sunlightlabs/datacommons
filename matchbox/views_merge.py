import time
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson as json
from dcentity.models import Entity, entityref_cache, MergeCandidate
from matchbox.utils import decode_htmlentities
from dcentity.queries import search_entities_by_name, merge_entities
import urllib

ENTITY_TYPES = getattr(settings, 'ENTITY_TYPES', ())

@login_required
def dashboard(request):
    """ Display user dashboard
        - queue items
        - saved searches
        - recent commits
    """
    merge_queue = MergeCandidate.objects.pending(request.user)
    data = {
        'merge_queue': merge_queue,
    }
    return render_to_response('matchbox/merge/index.html', data, context_instance=RequestContext(request))

def _search(query, type_filter):        
    results = []
    for (id_, name, count, total_given, total_received) in search_entities_by_name(query, [type_filter]):
        results.append({
            'id': id_,
            'type': 'organization',
            'name': name,
            'count': count,
            'total_given': float(total_given),
            'total_received': float(total_received)
        })
    content = json.dumps(results)
    
    return HttpResponse(content, mimetype='application/javascript')



@login_required
def search(request):
    return _search(decode_htmlentities(request.GET.get('q','')),request.GET.get('type_filter', ''),)

@login_required
def debug_search(request):
    _search(
        decode_htmlentities(request.GET.get('q','')),
        request.GET.get('type_filter', ''),
    )
    return render_to_response('matchbox/base.html')

@login_required
def queue(request, queue_id):
    item = MergeCandidate.objects.get(pk=queue_id)
    item.lock(request.user)
    return _search(item.name)
    

@login_required
def merge(request):
    
    if request.method == 'POST':        
        
        entity_ids = request.POST.getlist('entities')
        if len(entity_ids) > 1:
            
            old_names = Entity.objects.filter(id__in=entity_ids).order_by('name').values_list('name', flat=True)
            old_names = ["'%s'" % str(n) for n in old_names]
            
            e = Entity(name=request.POST['new_name'], type=request.POST['new_type'])
            merge_entities(entity_ids, e)
        
        params = []
        params.extend([('q', q) for q in request.POST.getlist('query')])
        
        for q in request.POST.getlist('queue'):
            MergeCandidate.objects.delete(pk=q)
            params.append(('queue', q))
            
        if 'new_type' in request.POST:
            params.append(('type_filter', request.POST['new_type']))
        qs = urllib.urlencode(params)
        
        return HttpResponseRedirect("%s?%s" % (reverse('matchbox_merge'), qs))
        
    else:
        
        queries = request.GET.getlist('q')
        queues = request.GET.getlist('queue')
        data = { 'queries': queries, 'queues': queues }
    
        type_ = request.GET.get('type_filter', '')
        if type_ in ENTITY_TYPES:
            data['type_filter'] = type_
            
        data['has_query'] = queries or queues
        
        return render_to_response('matchbox/merge/merge.html',
                                  data,
                                  context_instance=RequestContext(request))

@login_required
def google_search(request):
    """ Send search to Google.
        Log the search in the future.
    """
    query = request.GET.get('q', '')
    return HttpResponseRedirect('http://google.com/search?q=%s' % query)

