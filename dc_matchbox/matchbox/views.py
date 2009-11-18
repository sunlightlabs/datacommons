from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from matchbox.models import Entity, entityref_cache, MergeCandidate
from matchbox.utils import decode_htmlentities
from queries import search_entities_by_name, search_transactions_by_entity, transaction_result_columns, merge_entities
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
    # results = []
    # for res in Entity.objects.filter(name__icontains=query, type=type_filter):
    #    e = {
    #        'id': res.id,
    #        'type': res.type,
    #        'name': res.name,
    #        'count': res.count,
    #        'notes': 0,
    #    }
    #    e['html'] = render_to_string('matchbox/partials/entity_row.html', {'entity': res})
    #    results.append(e)
    # content = json.dumps(results)
    # return HttpResponse(content, mimetype='application/javascript')
    results = []
    for (id_, name, count) in search_entities_by_name(query, type_filter):
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
    return _search(
        decode_htmlentities(request.GET.get('q','')),
        request.GET.get('type_filter', ''),
    )


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
            e = Entity(name=request.POST['new_name'], type=request.POST['type_filter'])
            merge_entities(entity_ids, e)
        
        params = []
        params.extend([('q', q) for q in request.POST.getlist('query')])
        
        for q in request.POST.getlist('queue'):
            MergeCandidate.objects.delete(pk=q)
            params.append(('queue', q))
            
        if 'type' in request.POST:
            params.append(('type_filter', request.POST['type']))
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












#
# Ethan's stuff
#

from django.template import Context, loader
from django import forms

def transactions_page(request):
    template = loader.get_template('transactions.html')
                                           
    if 'entity_id' in request.GET:                                       
        results = search_transactions_by_entity(request.GET['entity_id'])
        context = Context()
        context['results'] = results
        context['headers'] = transaction_result_columns
        
        return HttpResponse(template.render(context))
    else:
        return HttpResponse("Error: request should include entity_id parameter.")
    
    
    
class EntitiesForm(forms.Form):    
    query = forms.CharField(max_length = 40)
        
def entities_page(request):
    template = loader.get_template('entities.html')
    context = Context()
    context['action'] = 'entities'
    context['search_form'] = EntitiesForm()

    if request.method == 'POST':
        search_form = EntitiesForm(request.POST)
        if search_form.is_valid():
            results = search_entities_by_name(search_form.cleaned_data['query'])
            context['search_form'] = search_form
            context['results'] = results
            context['headers'] = ['name', 'count']
            
            return HttpResponse(template.render(context))
        else:
            return HttpResponse("Error: invalid form data")
    else:
        return HttpResponse(template.render(context))
    
