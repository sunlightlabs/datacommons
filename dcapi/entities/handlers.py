from time import time
import sys

from urllib import unquote_plus
from django.db.models import Q
from piston.handler import BaseHandler
from dcentity.models import Entity
from dcapi.aggregates.queries import search_names

class EntityHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Entity
    
    def read(self, request, entity_id):
        return Entity.objects.get(pk=entity_id)


class EntityFilterHandler(BaseHandler):
    allowed_methods = ('GET',)

    fields = ('id','name','type','timestamp','reviewer')
    model = Entity

    def read(self, request):
        search_string = request.GET.get('search', None)
        if not search_string:
            return {'response' : "It doesn't make any sense to do a search without a search string"}

        
        # entity_types is currently not supported but we'll probably
        # build it in at some point.
        entity_types = request.GET.get('type', None)        
        result = search_names(search_string, entity_types)
        
        results_annotated = []
        for (name, id_, type, count_given, count_received, total_given, total_received) in result:
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


