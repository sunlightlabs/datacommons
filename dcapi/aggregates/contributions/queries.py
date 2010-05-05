
from dcapi.aggregates.queries import *

         
    
get_top_sectors_to_cand_stmt = """
    select sector, count, amount
    from agg_sectors_to_cand
    where
        recipient_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""    

get_top_catorders_to_cand_stmt = """
    select contributor_category_order, count, amount
    from agg_cat_orders_to_cand
    where
        recipient_entity = %s
        and sector = %s
        and cycle = %s
    order by amount desc
    limit %s
"""    
    
get_top_orgs_to_cand_stmt = """
    select organization_name, organization_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from agg_orgs_to_cand
    where
        recipient_entity = %s
        and cycle = %s
    order by total_amount desc
    limit %s
"""

    
get_top_cands_from_indiv_stmt = """
    select recipient_name, recipient_entity, count, amount
    from agg_cands_from_indiv
    where
        contributor_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""    

get_top_orgs_from_indiv_stmt = """
    select recipient_name, recipient_entity, count, amount
    from agg_orgs_from_indiv
    where
        contributor_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""



get_top_cands_from_org_stmt = """
    select recipient_name, recipient_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from agg_cands_from_org
    where
        organization_entity = %s
        and cycle = %s
    order by total_amount desc
    limit %s
"""


get_party_from_indiv_stmt = """
    select recipient_party, count, amount
    from agg_party_from_indiv
    where
        contributor_entity = %s
        and cycle = %s
"""


get_party_from_org_stmt = """
    select recipient_party, count, amount
    from agg_party_from_org
    where
        organization_entity = %s
        and cycle = %s
"""


get_namespace_from_org_stmt = """
    select transaction_namespace, count, amount
    from agg_namespace_from_org
    where
        organization_entity = %s
        and cycle = %s
"""


get_local_to_politician_stmt = """
    select local, count, amount
    from agg_local_to_politician
    where
        recipient_entity = %s
        and cycle = %s
"""


get_contributor_type_to_politician_stmt = """
    select contributor_type, count, amount
    from agg_contributor_type_to_politician
    where
        recipient_entity = %s
        and cycle = %s
"""


search_stmt = """
    select e.id, e.name, e.type, a.contributor_count, a.recipient_count, a.contributor_amount, a.recipient_amount
    from matchbox_entity e
    join agg_entities a 
        on e.id = a.entity_id
    where 
        a.cycle = -1
    	and to_tsvector('datacommons', e.name) @@ to_tsquery('datacommons', %s)
		and (a.contributor_count > 0 or a.recipient_count > 0)
"""


get_entity_totals_stmt = """
    select contributor_count, recipient_count, contributor_amount, recipient_amount
    from agg_entities e
    where
        entity_id = %s
        and cycle = %s
"""



def search_names(query, entity_types=[]):
    # entity_types is not currently used but we'll build it in at some
    # point...
    
    parsed_query = ' & '.join(query.split(' '))
    
    return execute_top(search_stmt, parsed_query)


def get_top_sectors_to_cand(candidate, cycle, limit):
    return execute_top(get_top_sectors_to_cand_stmt, candidate, cycle, limit)

def get_top_catorders_to_cand(candidate, sector, cycle, limit):
    return execute_top(get_top_catorders_to_cand_stmt, candidate, sector, cycle, limit)

def get_top_cands_from_indiv(individual, cycle, limit):
    return execute_top(get_top_cands_from_indiv_stmt, individual, cycle, limit)
    
def get_top_orgs_from_indiv(individual, cycle, limit):
    return execute_top(get_top_orgs_from_indiv_stmt, individual, cycle, limit)

def get_top_orgs_to_cand(candidate, cycle, limit):
    return execute_top(get_top_orgs_to_cand_stmt, candidate, cycle, limit)

def get_top_cands_from_org(organization, cycle, limit):
    return execute_top(get_top_cands_from_org_stmt, organization, cycle, limit)


def get_party_from_indiv(individual, cycle):
    return execute_pie(get_party_from_indiv_stmt, individual, cycle)

def get_party_from_org(organization, cycle):
    return execute_pie(get_party_from_org_stmt, organization, cycle)

def get_namespace_from_org(organization, cycle):
    return execute_pie(get_namespace_from_org_stmt, organization, cycle)

def get_local_to_cand(candidate, cycle):
    return execute_pie(get_local_to_politician_stmt, candidate, cycle)

def get_contributor_type_to_cand(candidate, cycle):
    return execute_pie(get_contributor_type_to_politician_stmt, candidate, cycle)


def get_entity_totals(entity_id, cycle):
    result = execute_one(get_entity_totals_stmt, entity_id, cycle)
    
    if not result:
        return [0, 0, 0, 0]
    return result



