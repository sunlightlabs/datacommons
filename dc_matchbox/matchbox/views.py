from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
import json

ENTITY_TYPES = getattr(settings, 'ENTITY_TYPES', ())

@login_required
def dashboard(request):
    return render_to_response('matchbox/dashboard.html')

@login_required
def search(request):
    if 'query' in request.GET:
        results = [{
                    'id': id,
                    'type': 'organization',
                    'name': name,
                    'count': count,
                    'notes': 0
                    } for (id, name, count) in search_entities_by_name(request.GET['query'])]
        
    else:
        results = []
        
    for result in results:
            result['html'] = render_to_string('matchbox/partials/entity_row.html', {'entity': result})
    content = json.dumps(results)
    return HttpResponse(content, mimetype='application/javascript')

@login_required
def queue(request, queue_id):
    pass

@login_required
def merge(request):
    
    if request.method == 'POST':
    
        pass
        
    else:
    
        data = { }
    
        type_ = request.GET.get('type', '')
        if type_ in ENTITY_TYPES:
            data['entity_type'] = type_
        
        return render_to_response('matchbox/merge.html', data)

@login_required
def google_search(request):
    query = request.GET.get('q', '')
    if not query.startswith('"'):
        query = '"%s"' % query
    return HttpResponseRedirect('http://google.com/search?q=%s' % query)


""" Ethan's stuff """

from django.template import Context, loader
from django import forms

from queries import search_entities_by_name, search_transactions_by_entity, transaction_result_columns

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
    
