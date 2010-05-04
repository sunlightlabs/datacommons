from dcapi.aggregates.contributions.queries import search_names,\
    get_entity_totals
from dcentity.models import Entity, EntityAttribute
from django.db.models import Q
from piston.handler import BaseHandler
from time import time
from urllib import unquote_plus
import sys
from dcapi.aggregates.queries import DEFAULT_CYCLE


class EntityHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Entity
    
    fields = Entity._meta.get_all_field_names()
    
    def read(self, request, entity_id):
        return Entity.objects.get(pk=entity_id)


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
        search_string = request.GET.get('search', None)
        if not search_string:
            return {'response' : "It doesn't make any sense to do a search without a search string"}

        
        # entity_types is currently not supported but we'll probably
        # build it in at some point.
        entity_types = request.GET.get('type', None)        
        result = search_names(search_string, entity_types)
        
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

class EntityTotalsHandler(BaseHandler):
    allowed_methods = ['GET']
    
    fields = ['contributor_count', 'recipient_count', 'contributor_amount', 'recipient_amount']
    
    def read(self, request, entity_id):
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)
        
        result = get_entity_totals(entity_id, cycle)
        
        return dict(zip(self.fields, result)) if result else None
            
