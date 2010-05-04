
from piston.handler import BaseHandler
from dcapi.aggregates.queries import ALL_CYCLES, DEFAULT_LIMIT
import traceback


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