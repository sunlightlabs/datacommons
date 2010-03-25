from time import time
import sys

from urllib import unquote_plus
from django.db.models import Q
from piston.handler import BaseHandler
from dcentity.models import Entity
from dcentity.queries import search_entities_by_name

class EntityHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Entity
    
    def read(self, request, entity_id):
        return Entity.objects.get(pk=entity_id)

class EntityFilterHandler(BaseHandler):
    allowed_methods = ('GET',)
#    fields = ('id','name','type','timestamp','reviewer',
#              ('attributes',('namespace','value')),
#              ('aliases',('alias',))
#              )
    fields = ('id','name','type','timestamp','reviewer')
    model = Entity

    def read(self, request):
        search_string = request.GET.get('search', None)
        if not search_string:
            return {'response' : "It doesn't make any sense to do a search without a search string"}

        entity_types = request.GET.get('type', None)
        # search_entities_by_name expects a list for the type filter,
        # even if there's only one element.
        if entity_types:
            entity_types = [entity_type.strip() for entity_type in entity_types.split(',')]
        return search_entities_by_name(search_string, entity_types)


#        results = []
#        for (id_, name, count, total_given, total_received) in search_entities_by_name(search_string, entity_types):
#            results.append({
#                    'id': id_,
#                    'type': 'organization',
#                    'name': name,
#                    'count': count,
#                    'total_given': float(total_given),
#                    'total_received': float(total_received)
#                    })
#        return results
        


