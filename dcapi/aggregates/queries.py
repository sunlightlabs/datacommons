
from django.db import connection
         
            
get_top_indivs_to_cand_stmt = """
    select contributor_name, contributor_entity, count, amount
    from agg_indivs_to_cand_by_cycle
    where
        recipient_entity = %s
        and cycle = %s
    order by amount desc
        limit %s
"""
    
get_top_cmtes_to_cand_stmt = """
    select contributor_name, contributor_entity, count, amount
    from agg_cmtes_to_cand_by_cycle
    where
        recipient_entity = %s
        and cycle = %s
    order by amount desc
        limit %s
"""
    
get_top_cats_to_cand_stmt = """
    select contributor_category, count, amount
    from agg_cats_to_cand_by_cycle
    where
        recipient_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""    

get_top_catorders_to_cand_stmt = """
    select contributor_category_order, count, amount
    from agg_cat_orders_to_cand_by_cycle
    where
        recipient_entity = %s
        and contributor_category = %s
        and cycle = %s
    order by amount desc
    limit %s
"""    
    
    
get_top_cands_from_indiv_stmt = """
    select recipient_name, recipient_entity, count, amount
    from agg_cands_from_indiv_by_cycle
    where
        contributor_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""    

get_top_cmtes_from_indiv_stmt = """
    select recipient_name, recipient_entity, count, amount
    from agg_cmtes_from_indiv_by_cycle
    where
        contributor_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""

get_top_cands_from_cmte_stmt = """
    select recipient_name, recipient_entity, count, amount
    from agg_cands_from_cmte_by_cycle
    where
        contributor_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""

get_top_indivs_to_cmte_stmt = """
    select contributor_name, contributor_entity, count, amount
    from agg_indivs_to_cmte_by_cycle
    where
        recipient_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""



search_stmt = """
    select e.id, e.name, e.type, a.contributor_count, a.recipient_count, a.contributor_amount, a.recipient_amount
    from matchbox_entity e
    join agg_entities a 
        on e.id = a.entity_id
    where 
		to_tsvector('datacommons', e.name) @@ to_tsquery('datacommons', %s)
		and (a.contributor_count > 0 or a.recipient_count > 0)
"""


def search_names(query, entity_types=[]):
    # entity_types is not currently used but we'll build it in at some
    # point...
    
    parsed_query = ' & '.join(query.split(' '))
    
    return _execute(search_stmt, parsed_query)


def _execute(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return list(cursor)


def get_top_cmtes_to_cand(candidate, cycle, limit):
    return _execute(get_top_cmtes_to_cand_stmt, candidate, cycle, limit)

def get_top_indivs_to_cand(candidate, cycle, limit):
    return _execute(get_top_indivs_to_cand_stmt, candidate, cycle, limit)

def get_top_cats_to_cand(candidate, cycle, limit):
    return _execute(get_top_cats_to_cand_stmt, candidate, cycle, limit)

def get_top_catorders_to_cand(candidate, category, cycle, limit):
    return _execute(get_top_catorders_to_cand_stmt, candidate, category, cycle, limit)

def get_top_cands_from_indiv(individual, cycle, limit):
    return _execute(get_top_cands_from_indiv_stmt, individual, cycle, limit)
    
def get_top_cmtes_from_indiv(individual, cycle, limit):
    return _execute(get_top_cmtes_from_indiv_stmt, individual, cycle, limit)

def get_top_cands_from_cmte(org, cycle, limit):
    return _execute(get_top_cands_from_cmte_stmt, org, cycle, limit)

def get_top_indivs_to_cmte(org, cycle, limit):
    return _execute(get_top_indivs_to_cmte_stmt, org, cycle, limit)



