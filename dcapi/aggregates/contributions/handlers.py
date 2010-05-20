
from dcapi.aggregates.handlers import TopListHandler, PieHandler



class OrgPartyBreakdownHandler(PieHandler):
    
    category_map = {'R': 'Republicans', 'D': 'Democrats'}
    
    stmt = """
        select recipient_party, count, amount
        from agg_party_from_org
        where
            organization_entity = %s
            and cycle = %s
    """
    
class OrgLevelBreakdownHandler(PieHandler):

    category_map = {'urn:fec:transaction': 'Federal', 'urn:nimsp:transaction': 'State'}
    
    stmt = """
        select transaction_namespace, count, amount
        from agg_namespace_from_org
        where
            organization_entity = %s
            and cycle = %s
    """

class PolLocalBreakdownHandler(PieHandler):
    
    stmt = """
        select local, count, amount
        from agg_local_to_politician
        where
            recipient_entity = %s
            and cycle = %s
    """
    
class PolContributorTypeBreakdownHandler(PieHandler):
    
    category_map = {'I': 'Individuals', 'C': 'PACs'}
    
    stmt = """
        select contributor_type, count, amount
        from agg_contributor_type_to_politician
        where
            recipient_entity = %s
            and cycle = %s
    """

class IndivPartyBreakdownHandler(PieHandler):

    category_map = {'R': 'Republicans', 'D': 'Democrats'}
    
    stmt = """
        select recipient_party, count, amount
        from agg_party_from_indiv
        where
            contributor_entity = %s
            and cycle = %s
    """
        

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
    

class IndustriesBySectorHandler(TopListHandler):
    
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




