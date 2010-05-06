
from django.db import connection
from piston.handler import BaseHandler
import traceback


# at the database level -1 is used to indicate summation over all cycles
ALL_CYCLES = '-1'
DEFAULT_LIMIT = '10'
DEFAULT_CYCLE = ALL_CYCLES


        
def execute_one(stmt, fields, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return dict(zip(fields, cursor.fetchone()))

def execute_top(stmt, fields, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return [dict(zip(fields, row)) for row in cursor]

def execute_pie(stmt, _, *args):
    result_rows = execute_top(stmt, *args)
    return dict([(category, (count, amount)) for (category, count, amount) in result_rows])
        
        
execution = {'top': execute_top,
             'one': execute_one,
             'pie': execute_pie}        
        
class SQLHandler(BaseHandler):
    
    allowed_methods = ['GET']
    
    # these four fields must be filled in by subclass
    args = None
    stmt = None
    exec_type = None
    
    def read(self, request, **kwargs):
        # todo: handle error properly
        assert(set(self.args) == set(kwargs.keys()))
        
        return execution[self.exec_type](self.stmt, self.fields, *[kwargs[param] for param in self.args])
        
        

class TopListHandler(BaseHandler):
    
    args = ['entity_id', 'cycle', 'limit']
    fields = None
    stmt = None
    
    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)}) 
        kwargs.update({'limit': request.GET.get('limit', DEFAULT_LIMIT)})    
        
        raw_result = execute_top(self.stmt, self.fields, *[kwargs[param] for param in self.args])
    
        return [dict(zip(self.fields, row)) for row in raw_result]


class PieHandler(BaseHandler):
    
    args = ['entity_id', 'cycle']
    category_map = {}
    stmt = None
    
    
    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)}) 
        
        raw_result = execute_pie(self.stmt, *[kwargs[param] for param in self.args])
        
        return dict([(self.category_map[key], value) if key in self.category_map else (key, value) for (key, value) in raw_result.items() ])
 
    