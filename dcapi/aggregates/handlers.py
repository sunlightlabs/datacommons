
from dcentity.models import Entity
from django.db import connection
from piston.handler import BaseHandler
from piston.utils import rc


# at the database level -1 is used to indicate summation over all cycles
ALL_CYCLES = '-1'
DEFAULT_LIMIT = '10'
DEFAULT_CYCLE = ALL_CYCLES


def execute_top(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return list(cursor)

def execute_pie(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return dict([(category, (count, amount)) for (category, count, amount) in cursor])
        
def execute_one(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return cursor.fetchone()


def handle_empty_result(entity_id):
    """ Empty results are normally fine, expect when the entity ID doesn't exist at all--then return 404. """
    
    if Entity.objects.filter(id=entity_id).count() != 1:
        error_response = rc.NOT_FOUND
        error_response.write('No entity with the given ID.')
        return error_response
    
    return []



class TopListHandler(BaseHandler):
    
    args = ['entity_id', 'cycle', 'limit']
    fields = None
    stmt = None
    
    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)}) 
        kwargs.update({'limit': request.GET.get('limit', DEFAULT_LIMIT)})    
        
        raw_result = execute_top(self.stmt, *[kwargs[param] for param in self.args])
        
        if not raw_result:
            return handle_empty_result(kwargs['entity_id'])
    
        return [dict(zip(self.fields, row)) for row in raw_result]


class PieHandler(BaseHandler):
    
    args = ['entity_id', 'cycle']
    category_map = {}
    stmt = None
    
    
    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)}) 
        
        raw_result = execute_pie(self.stmt, *[kwargs[param] for param in self.args])
        
        if not raw_result:
            return handle_empty_result(kwargs['entity_id'])        
        
        return dict([(self.category_map[key], value) if key in self.category_map else (key, value) for (key, value) in raw_result.items() ])
 
    