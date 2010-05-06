from dcapi.aggregates.entities.queries import search_names, get_entity_totals
from dcapi.aggregates.handlers import DEFAULT_CYCLE, ALL_CYCLES
from dcentity.models import Entity, EntityAttribute
from django.db.models import Q
from piston.handler import BaseHandler
from time import time
from urllib import unquote_plus
import sys


class EntityHandler(BaseHandler):
    allowed_methods = ('GET',)
    #model = Entity
    
    totals_fields = ['contributor_count', 'recipient_count', 'contributor_amount', 'recipient_amount']
    ext_id_fields = ['namespace', 'id']
    #fields = ['name', 'id', ['contributions'] + totals_fields, ['external_ids'] + ext_id_fields]
    
    def read(self, request, entity_id):
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)

        entity = Entity.objects.select_related().get(id=entity_id)
        totals = dict(zip(self.totals_fields, get_entity_totals(entity_id, cycle)))
        external_ids = [{'namespace': attr.namespace, 'id': attr.value} for attr in entity.attributes.all()]
        
        result = {'name': entity.name,
                  'id': entity.id,
                  'contributions': totals,
                  'external_ids': external_ids}
        
        if cycle != ALL_CYCLES:
            result.update({'cycle': cycle})
            
        return result


class EntityAttributeHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ['id']
    
    def read(self, request):
        namespace = request.GET.get('namespace', None)
        id = request.GET.get('id', None)
        
        if not id or not namespace:
            # to do: what's the proper way to do error handling in a handler?
            return {'response': 'Must provide a namespace and id.'}

        attributes = EntityAttribute.objects.filter(namespace = namespace, value = id, verified = 't')
        
        return [{'id': a.entity_id} for a in attributes]
    

class EntityFilterHandler(BaseHandler):
    allowed_methods = ('GET',)

    fields = ['id','name','type','count_given','count_received','total_given','total_received']

    def read(self, request):
        search_string = unquote_plus(request.GET.get('search', None))
        if not search_string:
            return {'response' : "It doesn't make any sense to do a search without a search string"}

        result = search_names(search_string)
        
        results_annotated = []
        for (id_, name, type, count_given, count_received, total_given, total_received) in result:
            results_annotated.append({
                    'id': id_,
                    'name': name,
                    'type': type,
                    'count_given': count_given,
                    'count_received': count_received,
                    'total_given': float(total_given),
                    'total_received': float(total_received)
                    })
        return results_annotated 
     
