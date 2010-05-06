
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




def get_top_sectors_to_cand(candidate, cycle, limit):
    return execute_top(get_top_sectors_to_cand_stmt, candidate, cycle, limit)

def get_top_catorders_to_cand(candidate, sector, cycle, limit):
    return execute_top(get_top_catorders_to_cand_stmt, candidate, sector, cycle, limit)

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




