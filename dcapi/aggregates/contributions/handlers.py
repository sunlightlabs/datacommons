from queries import get_top_catorders_to_cand, \
    get_top_orgs_from_indiv, get_top_cands_from_indiv, get_top_cands_from_org, \
    get_top_sectors_to_cand, get_party_from_indiv, get_party_from_org, \
    get_namespace_from_org, get_local_to_cand, get_contributor_type_to_cand, \
    get_top_orgs_to_cand
from piston.handler import BaseHandler
from piston.utils import rc
import traceback
from dcapi.aggregates.queries import DEFAULT_LIMIT, DEFAULT_CYCLE



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



################################### NEW HANDLERS #########################

class OrgRecipientsBreakdownHandler(BaseHandler):
    ''' Breakdown of recipients from a single org'''
    allowed_methods = ('GET',)
    fields = ['name', 'id', 'count', 'amount', 'type']    
    def read(self, request, entity_id):        
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)

        # a single type of breakdown must be specified
        breakdown_type = request.GET.get('type', None)
        if breakdown_type == 'party':
            query = get_party_from_org
        elif breakdown_type == 'level':
            query = get_namespace_from_org
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid API Call Parameters to org recipients breakdown: valid breakdown type must be specified. ")
            return response

        try:
            results = query(entity_id, cycle)
            if breakdown_type == 'party':
                # the raw database labels aren't very useful so make
                # them a little nice
                annotated = {}
                for k,v in results.iteritems():
                    if k == 'R':
                        annotated['Republicans'] = results['R']
                    elif k == 'D':
                        annotated['Democrats'] = results['D']
                results = annotated
            elif breakdown_type == 'level':
                # the raw database labels aren't very useful so make
                # them a little nicer                
                annotated = {}
                for k,v in results.iteritems():
                    if k == 'urn:fec:transaction':
                        annotated['Federal'] = results['urn:fec:transaction']
                    elif k == 'urn:nimsp:transaction':
                        annotated['State'] = results['urn:nimsp:transaction']
                results = annotated
            return results
        except:
            traceback.print_exc() 
            raise

class PolContributorsBreakdownHandler(BaseHandler):
    ''' Breakdown of recipients from a single org'''
    allowed_methods = ('GET',)
    fields = ['name', 'id', 'count', 'amount', 'type']    
    def read(self, request, entity_id):        
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)

        # a single type of breakdown must be specified
        breakdown_type = request.GET.get('type', None)
        if breakdown_type == 'local':
            query = get_local_to_cand
        elif breakdown_type == 'entity':
            query = get_contributor_type_to_cand
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid API Call Parameters to org recipients breakdown: valid breakdown type must be specified. ")
            return response

        try:
            results = query(entity_id, cycle)
            if breakdown_type == 'entity':
                # the raw database labels aren't very useful so make
                # them a little nicer
                annotated = {}
                for k,v in results.iteritems():                   
                    if k == 'I':                        
                        annotated['Individuals'] = results['I']
                    elif k == 'C':
                        annotated['PACs'] = results['C']
                results = annotated
            return results
        except:
            traceback.print_exc() 
            raise

class IndivRecipientsBreakdownHandler(BaseHandler):
    ''' Breakdown of recipients from a single individual'''
    allowed_methods = ('GET',)
    fields = ['name', 'id', 'count', 'amount', 'type']    
    def read(self, request, entity_id):        
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)

        # a single type of breakdown must be specified
        breakdown_type = request.GET.get('type', None)
        if breakdown_type == 'party':
            query = get_party_from_indiv
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid API Call Parameters to org recipients breakdown: valid breakdown type must be specified. ")
            return response

        try:
            return query(entity_id, cycle)
        except:
            traceback.print_exc() 
            raise
        

class PolContributorsHandler(BaseHandler):
    ''' Contributors to a single politician'''

    allowed_methods = ('GET',)
    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']    
    def read(self, request, entity_id):        
        limit = request.GET.get('limit', DEFAULT_LIMIT)        
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)

        try:
            results = get_top_orgs_to_cand(entity_id, cycle, limit)
            return [dict(zip(self.fields, row)) for row in results]
        
        except:
            traceback.print_exc() 
            raise

class IndivRecipientsHandler(BaseHandler):
    ''' Recipients from a single individual'''

    allowed_methods = ('GET',)
    fields = ['name', 'id', 'count', 'amount', 'type']    
    def read(self, request, entity_id):        
        limit = request.GET.get('limit', DEFAULT_LIMIT)        
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)

        # if one or more specific recipient types were not specified,
        # then search them all. otherwise they should be passed in as
        # a comma-separated list.
        try:
            entity_types = request.GET.get('type', 'org, pol')
            types_list = [entity.strip() for entity in entity_types.split(',')]
            results = []
            for _type in types_list:
                if _type == 'org':
                    _type = 'organization'
                    query = get_top_orgs_from_indiv
                elif _type == 'pol':
                    _type = 'politician' # more user friendly for reading
                    query = get_top_cands_from_indiv
                else:                
                    response = rc.BAD_REQUEST
                    response.write("Invalid API Call Parameters: %s" % entity_types)
                    return response
                    
                # add the entity_type to the information returned
                query_results = [item+(_type,) for item in list(query(entity_id, cycle, limit))]
                results.extend(query_results)                
            annotated = []
            for (name, id_, count, amount, _type) in results:
                annotated.append({
                        'name': name,
                        'id': id_,
                        'count': count,
                        'amount': float(amount),
                        'type': _type,
                        }) 
            return annotated
        
        except:
            traceback.print_exc() 
            raise


class OrgRecipientsHandler(BaseHandler):
    ''' Recipients from a single org'''

    allowed_methods = ('GET',)
    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']   
     
    def read(self, request, entity_id):        
        limit = request.GET.get('limit', DEFAULT_LIMIT)        
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)

        try:
            results = get_top_cands_from_org(entity_id, cycle, limit)
            return [dict(zip(self.fields, row)) for row in results]
        
        except:
            traceback.print_exc() 
            raise


class SectorsHandler(BaseHandler):
    allowed_methods=('GET',)    
    fields = ['sector_code', 'contributions_count', 'amount']
    def read(self, request, entity_id):
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)
        limit = request.GET.get('limit', DEFAULT_LIMIT)
        print 'sectors handler: entity id %s' % entity_id
        results = get_top_sectors_to_cand(entity_id, cycle, limit)
        annotated = []
        for (name, count, amount) in results:
            annotated.append({
                    'sector_code': name,
                    'contributions_count': count,
                    'amount': float(amount),
                    })
        return annotated


class IndustriesBySectorHandler(BaseHandler):
    allowed_methods=('GET',)    
    fields = ['industry_code', 'contributions_count', 'amount']
    def read(self, request, entity_id, sector_id):
        cycle = request.GET.get('cycle', DEFAULT_CYCLE)
        limit = request.GET.get('limit', DEFAULT_LIMIT)
        results = get_top_catorders_to_cand(entity_id, sector_id, cycle, limit)
        annotated = []
        for (name, count, amount) in results:
            annotated.append({
                    'industry_code': name,
                    'contributions_count': count,
                    'amount': float(amount),
                    })
        return annotated



