
import time
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from matchbox.models import Entity, entityref_cache, MergeCandidate, EntityNote
from matchbox.utils import decode_htmlentities
from queries import search_entities_by_name, merge_entities
import json
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
    return render_to_response('matchbox/dashboard.html', data, context_instance=RequestContext(request))

def _search(query, type_filter):
    def run_logged_search():
        start_time = time.time()
        result = list(search_entities_by_name(query, type_filter))
        runtime = time.time() - start_time
        logging.info("Entity search for ('%s', '%s') returned %d results in %f seconds." % (query, type_filter, len(result), runtime))
        return result
        
    results = []
    for (id_, name, count) in run_logged_search():
        e = {
            'id': id_,
            'type': 'organization',
            'name': name,
            'count': count,
            'notes': 0,
        }
        e['html'] = render_to_string('matchbox/partials/entity_row.html', {'entity': Entity.objects.get(id=id_)})
        results.append(e)
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
            
            note_content = 'New entity created from merge of %s' % ", ".join(old_names)
            e.notes.add(EntityNote(user=request.user, content=note_content))
        
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
        
        return render_to_response('matchbox/merge.html',
                                  data,
                                  context_instance=RequestContext(request))


@login_required
def google_search(request):
    """ Send search to Google.
        Log the search in the future.
    """
    query = request.GET.get('q', '')
    return HttpResponseRedirect('http://google.com/search?q=%s' % query)


@login_required
def entity_detail(request, entity_id):
    """ Display entity detail page.
    """
    entity = Entity.objects.get(pk=entity_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            entity.name = name
        entity.save()
        return HttpResponseRedirect(reverse('matchbox_entity', args=(entity.id,)))
    else:
        transactions = { }
        for model in entityref_cache.iterkeys():
            if hasattr(model.objects, 'with_entity'):
                transactions[model.__name__] = model.objects.with_entity(entity).order_by('-amount')[:50]
        return render_to_response('matchbox/entity_detail.html', {
                                      'entity': entity,
                                      'transactions': transactions
                                  }, context_instance=RequestContext(request))


@login_required
def entity_transactions(request, entity_id):
    """ Return transactions partial for an entity.
    """
    entity = Entity.objects.get(pk=entity_id)
    transactions = { }
    for model in entityref_cache.iterkeys():
        if hasattr(model.objects, 'with_entity'):
            transactions[model.__name__] = model.objects.with_entity(entity).order_by('-amount')[:50]
    return render_to_response('matchbox/partials/entity_transactions.html', {
                                  'entity': entity,
                                  'transactions': transactions
                              }, context_instance=RequestContext(request))

@login_required
def entity_notes(request, entity_id):
    entity = Entity.objects.get(pk=entity_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            note = EntityNote(user=request.user, content=content)
            entity.notes.add(note)
            data = {'note': note}
            return render_to_response('matchbox/partials/entity_note.html', data)
    else:
        return HttpResponse('these are not the notes you are looking for')
    
