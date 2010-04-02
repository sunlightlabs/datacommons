
from django.db import connection, transaction

         
            
get_top_cmtes_to_cand_stmt = """
    select contributor_name, contributor_entity, sum(count), sum(amount)
    from agg_cmte_to_cand
    where
        recipient = %%s
        -- possible cycle restriction:
        %s
    group by contributor_name, contributor_entity
    order by sum(amount) desc
    limit %%s
"""


get_top_indivs_to_cand_stmt = """
    select contributor_name, contributor_entity, sum(count), sum(amount)
    from agg_indiv_to_cand
    where
        recipient = %%s
        -- possible cycle restriction:        
        %s
    group by contributor_name, contributor_entity
    order by sum(amount) desc
        limit %%s
"""
    
    
get_top_cats_to_cand_stmt = """
    select contributor_category, sum(count) as count, sum(amount) as amount
    from agg_cat_to_cand
    where
        recipient = %%s
        -- possible cycle restriction:        
        %s
    group by contributor_category
    order by sum(amount) desc
    limit %%s
"""    

get_top_catorders_to_cand_stmt = """
    select contributor_category_order, sum(count), sum(amount)
    from agg_cat_to_cand
    where
        recipient = %%s
        and contributor_category = %%s
        -- possible cycle restriction:        
        %s
    group by contributor_name, contributor_entity
    order by sum(amount) descc
    limit %%s
"""    
    
    
get_top_cands_from_indiv_stmt = """
    select recipient_name, recipient_entity, sum(count), sum(amount)
    from agg_indiv_to_cand
    where
        contributor = %%s
        -- possible cycle restriction:
        %s
    group by recipient_name, recipient_entity
    order by sum(amount) desc
    limit %%s
"""    

get_top_cmtes_from_indiv_stmt = """
    select recipient_name, recipient_entity, sum(count), sum(amount)
    from agg_indiv_to_cmte   
    where
        contributor = %%s
        -- possible cycle restriction:
        %s
    group by recipient_name, recipient_entity
    order by sum(amount) desc
    limit %%s
"""


search_stmt = """
    (select coalesce(c.name, r.name) as name, '' as entity_id, coalesce(c.count, 0) as count_given, coalesce(r.count, 0) as count_received, coalesce(c.given, 0) as given, coalesce(r.received, 0) as received
    from
        (select contributor as name, '' as entity_id, sum(count) as count, sum(amount) as given
        from agg_contributions
        where to_tsvector('datacommons', contributor) @@ to_tsquery('datacommons', %s)
        group by contributor
        having sum(count) > 0) as c    
    full join    
        (select recipient as name, '' as entity_id, sum(count) as count, sum(amount) as received
        from agg_contributions
        where to_tsvector('datacommons', recipient) @@ to_tsquery('datacommons', %s)
        group by recipient
        having sum(count) > 0) as r
    on c.name = r.name)
union
    (select *
    from agg_entities
    where 
		to_tsvector('datacommons', name) @@ to_tsquery('datacommons', %s)
		and (contributor_count > 0 or recipient_count > 0))
"""


def search_names(query, entity_types):
    # entity_types is not currently used but we'll build it in at some
    # point...

    cursor = connection.cursor()
    
    parsed_query = ' & '.join(query.split(' '))
    
    cursor.execute(search_stmt, [parsed_query, parsed_query, parsed_query])
    return list(cursor)
    
#    
#    results_annotated = []
#    for (name, id_, count_given, count_received, total_given, total_received) in results:
#        results_annotated.append({
#                'id': id_,
#                'name': name,
#                'count_given': count_given,
#                'count_received': count_received,
#                'total_given': float(total_given),
#                'total_received': float(total_received)
#                })
#    return results_annotated
#   


def _cycle_clause(cycles):
    return "cycle in (%s)" % (", ".join(["'%d'" % int(cycle) for cycle in cycles])) if cycles else ""

def _generic_top(stmt, entity, cycles, limit):
    cursor = connection.cursor()
    cursor.execute(stmt % (_cycle_clause(cycles)), [entity, int(limit)])
    return list(cursor)

DEFAULT_CYCLES = None
DEFAULT_LIMIT = 10

def get_top_cmtes_to_cand(candidate, cycles=DEFAULT_CYCLES, limit=DEFAULT_LIMIT):
    return _generic_top(get_top_cmtes_to_cand_stmt, candidate, cycles, limit)

def get_top_indivs_to_cand(candidate, cycles=DEFAULT_CYCLES, limit=DEFAULT_LIMIT):
    return _generic_top(get_top_indivs_to_cand_stmt, candidate, cycles, limit)

def get_top_cats_to_cand(candidate, cycles=DEFAULT_CYCLES, limit=DEFAULT_LIMIT):
    return _generic_top(get_top_cats_to_cand_stmt, candidate, cycles, limit)

def get_top_catorders_to_cand(candidate, category, cycles=DEFAULT_CYCLES, limit=DEFAULT_LIMIT):
    cursor = connection.cursor()
    cursor.execute(get_top_catorders_to_cand_stmt % (_cycle_clause(cycles)), [candidate, category, int(limit)])
    return list(cursor)    

def get_top_cands_from_indiv(individual, cycles=DEFAULT_CYCLES, limit=DEFAULT_LIMIT):
    return _generic_top(get_top_cands_from_indiv_stmt, individual, cycles, limit)
    
def get_top_cmtes_from_indiv(individual, cycles=DEFAULT_CYCLES, limit=DEFAULT_LIMIT):
    return _generic_top(get_top_cmtes_from_indiv_stmt, individual, cycles, limit)



# just for use at the command line when setting up database
@transaction.commit_on_success
def setup_aggregates():
    transaction.set_dirty()
    cursor = connection.cursor()
    cursor.execute(create_contributor_assoc_stmt)
    cursor.execute(create_recipient_assoc_stmt)
    cursor.execute(create_agg_entities_stmt)
    cursor.execute(create_top_stmt)
    cursor.execute(create_top_cat_to_cand_stmt)
    cursor.execute(create_top_cmtes_to_cand_stmt)
    cursor.execute(create_top_indiv_to_cand_stmt)
    cursor.execute(create_top_indiv_to_cmte_stmt)
    
