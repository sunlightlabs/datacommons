from piston.handler import BaseHandler
from dcapi.aggregates.queries import get_top_indivs_to_cand,\
    get_top_cats_to_cand, get_top_cmtes_to_cand, get_top_cmtes_from_indiv,\
    get_top_cands_from_indiv


class TopContributorsHandler(BaseHandler):
    allowed_methods=('GET',)    
    # why is StreamingLoggingEmitter being used? Shouldn't be necessary to list fields.
    fields = ['name', 'id', 'count', 'amount']
    def read(self, request, entity_id):        
        n = request.GET.get('top', 10)
        
        print "reached handler."
        
        type = request.GET.get('type', None)
        if type == 'individual':
            query = get_top_indivs_to_cand
        # not implemented yet: industry search returns different result type
        #elif type = 'industry':
        #    query = get_top_cats_to_cand
        elif type == 'pac':
            query = get_top_cmtes_to_cand
        else:
            return {'Error': "Unrecognized or missing type: '%s'" % type} 

        print "Query function is %s" % query

        results = []
        for (name, id_, count, amount) in query(entity_id, limit=n):
            results.append({
                    'name': name,
                    'id': id_,
                    'count': count,
                    'amount': float(amount)
                    })
        return results

class TopRecipientsHandler(BaseHandler):
    allowed_methods=('GET',)    
    fields = ['name', 'id', 'count', 'amount']    
    def read(self, request, entity_id):        
        n = request.GET.get('top', 10)

        type = request.GET.get('type', None)
        if type == 'pac':
            query = get_top_cmtes_from_indiv
        elif type == 'politician':
            query = get_top_cands_from_indiv
        else:
            return {'Error': "Unrecognized or missing type: '%s'" % type} 

        results = []
        for (name, id_, count, amount) in query(entity_id, limit=10):
            results.append({
                    'name': name,
                    'id': id_,
                    'count': count,
                    'amount': float(amount)
                    })
        return results


class ContributionsBreakdownHandler(BaseHandler):
    allowed_methods=('GET',)    
    def read(self, request, entity_id):
        # 'breakdown' returns information about the percentage of
        # contributions from members of different categories.
        print 'HELLO WORLD'
        breakdown = request.GET.get('breakdown', None)    
        print breakdown
        if (breakdown == 'party' or breakdown == 'instate' 
            or breakdown == 'level' or breakdown == 'source'):
            return {"Unfortunately": "contributions breakdown API method not yet implemented"}

        else: # if breakdown category was not specified or was incorrect:
            return {'Error': 'Invalid API Call'}


class RecipientsBreakdownHandler(BaseHandler):
    allowed_methods=('GET',)    
    def read(self, request, entity_id):
        # 'breakdown' returns information about the percentage of
        # contributions from members of different categories.
        breakdown = request.GET.get('breakdown', None)    
        if breakdown in ['party', 'instate', 'level' 'source']:
            return {"Unfortunately": "Not Implemented"}

        else: # if breakdown category was not specified or was incorrect:
            return {"Unfortunately": "recipients breakdown API method not yet implemented"}

class MetadataHandler(BaseHandler):
    allowed_methods = ('GET',)
    def read(self, request, entity_id):
        return {"Unfortunately": "metadata API method not yet implemented"}


class DetailHandler(BaseHandler):
    allowed_methods = ('GET',)
    def read(self, request, entity_id):
        category = request.GET.get('category', None)
        if category not in ['industry', 'recipients', 'organizations']:
            return {'Error': 'Invalid API Call'}
        return {"Unfortunately": "detail API method not yet implemented"}


class TimelineHandler(BaseHandler):
    allowed_methods = ('GET',)
    def read(self, request, entity_id):
        # timeline can be specified by start and stop date, or by one or more cycles
        cycle = request.GET.get("cycle", None)
        start = request.GET.get("start", None)
        end = request.GET.get("end", None)
        
        return {"Unfortunately": "timeline API method not yet implemented"}





