from piston.handler import BaseHandler
from dcapi.aggregates.queries import get_top_contributors, get_top_recipients
from dcentity.queries import search_entities_by_name
try:
    import json
except:
    import simplejson as json

class TopContributorsHandler(BaseHandler):
    allowed_methods=('GET',)    
    def read(self, request, entity_id):        
        n = request.GET.get('top', None)

        # 'breakdown' returns information about the percentage of
        # contributions from members of different categories.
        breakdown = request.GET.get('breakdown', None)    
        print 'breakdown: %s' % breakdown
        if not breakdown:
            # get_top_contributors is hard coded to return 20 records
            # right now. eventually pass in n as a parameter. 
            results = []
            for (name, id_, count, amount) in get_top_contributors(entity_id):
                results.append({
                        'name': name,
                        'id': id_,
                        'count': count,
                        'amount': float(amount)
                        })
            return results

        elif (breakdown == 'party' or breakdown == 'instate' 
              or breakdown == 'level' or breakdown == 'source'):
            return {"response": "Not Implemented"}

        else:
            # this should be a 404?
            return {'response': 'Error: Invalid API Call'}

class TopRecipientsHandler(BaseHandler):
    allowed_methods=('GET',)    
    def read(self, request, entity_id):        

        # 'breakdown' returns information about the percentage of
        # contributions from members of different categories.
        breakdown = request.GET.get('breakdown', None)    
        if not breakdown:
            # get_top_contributors is hard coded to return 20 records
            # right now. eventually pass in n as a parameter. 
            results = []
            for (name, id_, count, amount) in get_top_recipients(entity_id):
                results.append({
                        'name': name,
                        'id': id_,
                        'count': count,
                        'amount': float(amount)
                        })
            return results


        elif (breakdown == 'party' or breakdown == 'instate' 
              or breakdown == 'level' or breakdown == 'source'):
            return {"response": "Not Implemented"}

        else:
            # this should be a 404?
            return {'response': 'Error: Invalid API Call'}




