from time import time
import sys

from urllib import unquote_plus
from django.db.models import Q
from piston.handler import BaseHandler
from matchbox.models import Entity
from matchbox.queries import search_entities_by_name

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

        entity_type = request.GET.get('type', None)
        if 'search' in request.GET:
            return search_entities_by_name(unicode(request.GET['search']), entity_type)
        


