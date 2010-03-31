
from django.db import connection

create_top_stmt = """
    create view agg_contributions as
        select case when contributor_entity = '' then contributor_name
                    else contributor_entity
               end as contributor,
               case when recipient_entity = '' then recipient_name
                    else recipient_entity
               end as recipient,
               contributor_type,
               recipient_type,
               transaction_type,
               contributor_category,
               contributor_category_order,
               cycle,
               count(*) as count,
               sum(amount) as amount
        from contribution_contribution
        group by case when contributor_entity = '' then contributor_name
                        else contributor_entity end,
                 case when recipient_entity = '' then recipient_name
                         else recipient_entity end,
                 contributor_type,
                 recipient_type,
                 transaction_type,
                 contributor_category,
                 contributor_category_order,
                 cycle
"""


create_top_cat_to_cand_stmt = """
    create view agg_cat_to_cand as
        select contributor_category, contributor_category_order, recipient, cycle, count, amount
        from agg_contributions
        where
            (contributor_type = 'C'
            and recipient_type = 'P'
            and transaction_type in ('24k', '24r', '24z'))
        or
            (contributor_type = 'I'
            and recipient_type = 'P'
            and transaction_type in ('11', '15', '15e', '15j', '22y'))        
"""

create_top_cmtes_to_cand_stmt = """
    create view agg_cmte_to_cand as
        select contributor, recipient, cycle, count, amount
        from agg_contributions
        where
            contributor_type = 'C'
            and recipient_type = 'P'
            and transaction_type in ('24k', '24r', '24z')
"""


create_top_indiv_to_cand_stmt = """
    create view agg_indiv_to_cand as
        select contributor, recipient, cycle, count, amount
        from agg_contributions
        where
            contributor_type = 'I'
            and recipient_type = 'P'
            and transaction_type in ('11', '15', '15e', '15j', '22y')
"""

create_top_indiv_to_cmte_stmt = """
    create view agg_indiv_to_cmte as
        select contributor, recipient, cycle, count, amount
        from agg_contributions
        where
            contributor_type = 'I'
            and recipient_type = 'C'
            -- any transaction_type restrictions?
"""
            
            
get_top_cmtes_to_cand_stmt = """
    select coalesce(e.name, contributor), coalesce(e.id, ''), count, amount
    from agg_cmte_to_cand
    left outer join matchbox_entity e
        on e.id = contributor
    where
        recipient = %%s
        -- possible cycle restriction:
        %s
    order by amount desc
    limit %%s
"""


get_top_indivs_to_cand_stmt = """
    select coalesce(e.name, contributor), coalesce(e.id, ''), count, amount
    from agg_indiv_to_cand
    left outer join matchbox_entity e
        on e.id = contributor
    where
        recipient = %%s
        -- possible cycle restriction:        
        %s
    order by amount desc
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
    select contributor_category_order, count, amount
    from agg_cat_to_cand
    where
        recipient = %%s
        and contributor_category = %%s
        -- possible cycle restriction:        
        %s
    order by amount desc
    limit %%s
"""    
    
    
get_top_cands_from_indiv_stmt = """
    select coalesce(e.name, recipient), coalesce(e.id, ''), count, amount
    from agg_indiv_to_cand
    left outer join matchbox_entity e
        on e.id = recipient
    where
        contributor = %%s
        -- possible cycle restriction:
        %s
    order by amount desc
    limit %%s
"""    

get_top_cmtes_from_indiv_stmt = """
    select coalesce(e.name, recipient), coalesce(e.id, ''), count, amount
    from agg_indiv_to_cmte
    left outer join matchbox_entity e
        on e.id = recipient   
    where
        contributor = %%s
        -- possible cycle restriction:
        %s
    order by amount desc
    limit %%s
"""

#

search_stmt = """
    (select coalesce(c.name, r.name) as name, '' as entity_id, coalesce(c.count, 0) + coalesce(r.count, 0) as count, coalesce(c.given, 0) as given, coalesce(r.received, 0) as received
    from
        (select contributor as name, '' as entity_id, sum(count) as count, sum(amount) as given, 0 as received
        from agg_contributions
        where to_tsvector('datacommons', contributor) @@ to_tsquery('datacommons', %s)
        group by contributor) as c    
    full join    
        (select recipient as name, '' as entity_id, sum(count) as count, 0 as given, sum(amount) as received
        from agg_contributions
        where to_tsvector('datacommons', recipient) @@ to_tsquery('datacommons', %s)
        group by recipient) as r
    on c.name = r.name)
union
    (select e.name, e.id, e.contribution_count, e.contribution_total_given, e.contribution_total_received
    from matchbox_entity e
    where to_tsvector('datacommons', name) @@ to_tsquery('datacommons', %s))
"""


def search_names(query, entity_types):
    # entity_types is not currently used but we'll build it in at some
    # point...

    cursor = connection.cursor()
    
    parsed_query = ' & '.join(query.split(' '))
    
    cursor.execute(search_stmt, [parsed_query, parsed_query, parsed_query])
    results = list(cursor)
    results_annotated = []
    for (name, id_, count, total_given, total_received) in results:
        results_annotated.append({
                'id': id_,
                'name': name,
                'count': count,
                'total_given': float(total_given),
                'total_received': float(total_received)
                })
    return results_annotated
   


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
def setup_aggregates():
    cursor = connection.cursor()
    cursor.execute(create_top_stmt)
    cursor.execute(create_top_cat_to_cand_stmt)
    cursor.execute(create_top_cmtes_to_cand_stmt)
    cursor.execute(create_top_indiv_to_cand_stmt)
    cursor.execute(create_top_indiv_to_cmte_stmt)
    
