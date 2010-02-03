from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import transaction
from matchbox.forms import AssociationForm
from matchbox.models import entityref_cache, Entity, EntityNote
from matchbox.queries import associate_transactions, disassociate_transactions
import re

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
        return render_to_response('matchbox/merge/entity_detail.html', {
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
            transactions[model.__name__] = model.objects.with_entity(entity)
    return render_to_response('matchbox/merge/partials/entity_transactions.html', {
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
            return render_to_response('matchbox/merge/partials/entity_note.html', data)
    else:
        return HttpResponse('these are not the notes you are looking for')

def parse_transaction_ids(clob):
    ids = []
    rows = (r.strip() for r in clob.split("\n"))
    for row in rows:
        if row:
            parts = re.split(r'[\,\t\s]', row, 1)
            parts = map(unicode.strip, parts)
            if len(parts) == 2 and parts[0].startswith('urn'):
                (ns, transaction) = parts
            elif len(parts) == 2 and parts[1].startswith('urn'):
                (transaction, ns) = parts
            elif len(parts) == 1 and row.startswith('urn'):
                (ns, transaction) = row.rsplit(':', 1)
            else:
                continue # big failure
            ids.append((ns, transaction))
    return ids

@login_required
@transaction.commit_on_success
def entity_associate(request, entity_id, model_name):
    (model, fields) = entityref_cache.for_model_name(model_name)
    entity = Entity.objects.get(pk=entity_id)
    if request.method == 'POST':
        form = AssociationForm(model, entity_id, request.POST)
        if form.is_valid():
            ids = parse_transaction_ids(form.cleaned_data['transactions'])
            if form.cleaned_data['action'] == 'add':
                for field in form.cleaned_data['fields']:
                    associate_transactions(entity_id, field, ids)
            elif form.cleaned_data['action'] == 'remove':
                for field in form.cleaned_data['fields']:
                    disassociate_transactions(field, ids)
    else:
        form = AssociationForm(model, entity_id)
    return render_to_response('matchbox/entity_associate.html', {'form': form, 'entity': entity}, context_instance=RequestContext(request))
