from dcapi.aggregates.contributions.queries import get_party_from_org, \
    get_namespace_from_org, get_local_to_cand, get_contributor_type_to_cand, \
    get_party_from_indiv
from dcapi.aggregates.handlers import DEFAULT_LIMIT, DEFAULT_CYCLE, \
    TopListHandler
from piston.handler import BaseHandler
from piston.utils import rc
import traceback



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
        

class PolContributorsHandler(TopListHandler):
    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']    

    stmt = """
        select organization_name, organization_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_orgs_to_cand
        where
            recipient_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """


class IndivOrgRecipientsHandler(TopListHandler):

    fields = ['recipient_name', 'recipient_entity', 'count', 'amount']    

    stmt = """
        select recipient_name, recipient_entity, count, amount
        from agg_orgs_from_indiv
        where
            contributor_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """


class IndivPolRecipientsHandler(TopListHandler):
    
    fields = ['recipient_name', 'recipient_entity', 'count', 'amount']    

    stmt = """
        select recipient_name, recipient_entity, count, amount
        from agg_cands_from_indiv
        where
            contributor_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """    


class OrgRecipientsHandler(TopListHandler):

    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']   
     
    stmt = """
        select recipient_name, recipient_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_cands_from_org
        where
            organization_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """


class SectorsHandler(TopListHandler):
    
    fields = ['sector', 'count', 'amount']
    
    stmt = """
        select sector, count, amount
        from agg_sectors_to_cand
        where
            recipient_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """
    

class IndustriesBySectorHandler(BaseHandler):
    
    args = ['entity_id', 'sector', 'cycle', 'limit']
    
    fields = ['industry', 'count', 'amount']
    
    stmt = """
        select contributor_category_order, count, amount
        from agg_cat_orders_to_cand
        where
            recipient_entity = %s
            and sector = %s
            and cycle = %s
        order by amount desc
        limit %s
    """    




