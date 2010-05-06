
from piston.handler import BaseHandler
from django.db import connection        

import traceback

# at the database level -1 is used to indicate summation over all cycles
ALL_CYCLES = '-1'
DEFAULT_LIMIT = '10'
DEFAULT_CYCLE = ALL_CYCLES


class AggTopHandler(BaseHandler):
    """ A basic implementation of a simple handler for any query method that takes an entity, a cycle and a limit.
    
        Implementations should set the 'fields' member to the returned fields, and a query method to call the SQL query.
    """
    
    allowed_methods = ['GET']
    
    def read(self, request, entity_id):
        try:
            cycle = request.GET.get('cycle', ALL_CYCLES)
            limit = request.GET.get('limit', DEFAULT_LIMIT)
            
            results = self.query(entity_id, cycle, limit)
            
            return [dict(zip(self.fields, row)) for row in results]

        except:
            traceback.print_exc() 
            raise
        
        
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
    fields = None
    stmt = None
    exec_type = None
    
    def read(self, request, **kwargs):
        return execution[self.exec_type](self.stmt, self.fields, *[kwargs[param] for param in self.args])
        
        

class TopListHandler(SQLHandler):
    
    args = ['entity_id', 'cycle', 'limit']
    fields = None
    stmt = None
    exec_type = 'top'
    
    def read(self, request, **kwargs):
        cycle = request.GET.get('cycle', ALL_CYCLES)
        limit = request.GET.get('limit', DEFAULT_LIMIT)        
        
        return super(TopListHandler,self).read(request, cycle=cycle, limit=limit, **kwargs)
    
    