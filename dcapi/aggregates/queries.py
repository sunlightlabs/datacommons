
from django.db import connection, transaction


create_contributor_assoc_stmt = """
    create view contributor_associations as
        select a.entity_id, c.transaction_id
        from contribution_contribution c
        inner join matchbox_entityalias a
            on c.contributor_name = a.alias
        where
            a.verified = 't'
        union    
        select a.entity_id, c.transaction_id
        from contribution_contribution c
        inner join matchbox_entityattribute a
            on c.contributor_ext_id = a.value
        where
            a.verified = 't'
            -- to do: and we'll need individual namespaces?
            and ((a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
                or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'))
"""


create_recipient_assoc_stmt = """
    create view recipient_associations as
        select a.entity_id, c.transaction_id
        from contribution_contribution c
        inner join matchbox_entityalias a
            on c.recipient_name = a.alias
        where
            a.verified = 't'
        union    
        select a.entity_id, c.transaction_id
        from contribution_contribution c
        inner join matchbox_entityattribute a
            on c.recipient_ext_id = a.value
        where
            a.verified = 't'
            and ((a.namespace = 'urn:crp:recipient' and c.transaction_namespace = 'urn:fec:transaction')
                or (a.namespace = 'urn:nimsp:recipient' and c.transaction_namespace = 'urn:nimsp:transaction'))
"""


create_top_stmt = """
    create view agg_contributions as
        select coalesce(ce.name, c.contributor_name) as contributor_name,
               ce.id as contributor_entity,
               coalesce(re.name, c.recipient_name) as recipient_name,
               re.id as recipient_entity,
               contributor_type,
               recipient_type,
               transaction_type,
               contributor_category,
               contributor_category_order,
               cycle,
               count(*) as count,
               sum(amount) as amount
        from contribution_contribution c
        left join contributor_associations ca using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        left join recipient_associations ra using (transaction_id)
        left join matchbox_entity re on re.id = ra.entity_id
        group by coalesce(ce.name, c.contributor_name),
                 ce.id,
                 coalesce(re.name, c.recipient_name),
                 re.id,
                 contributor_type,
                 recipient_type,
                 transaction_type,
                 contributor_category,
                 contributor_category_order,
                 cycle
"""


create_agg_entities_stmt = """
    create view agg_entities as
        select e.name, e.id, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count, coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
        from 
            matchbox_entity e
        left join
            (select a.entity_id, count(transaction), sum(transaction.amount)
            from contributor_associations a
            inner join contribution_contribution transaction using (transaction_id)
            group by a.entity_id) as contrib_aggs
            on contrib_aggs.entity_id = e.id
        left join
            (select a.entity_id, count(transaction), sum(transaction.amount)
            from recipient_associations a
            inner join contribution_contribution transaction using (transaction_id)
            group by a.entity_id) as recip_aggs
            on recip_aggs.entity_id = e.id
"""


create_top_cat_to_cand_stmt = """
    create view agg_cat_to_cand as
        select contributor_category, contributor_category_order, recipient_name, recipient_entity, cycle, count, amount
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
        select contributor_name, contibutor_entity, recipient_name, recipient_entity, cycle, count, amount
        from agg_contributions
        where
            contributor_type = 'C'
            and recipient_type = 'P'
            and transaction_type in ('24k', '24r', '24z')
"""


create_top_indiv_to_cand_stmt = """
    create view agg_indiv_to_cand as
        select contributor_name, contibutor_entity, recipient_name, recipient_entity, cycle, count, amount
        from agg_contributions
        where
            contributor_type = 'I'
            and recipient_type = 'P'
            and transaction_type in ('11', '15', '15e', '15j', '22y')
"""

create_top_indiv_to_cmte_stmt = """
    create view agg_indiv_to_cmte as
        select contributor_name, contibutor_entity, recipient_name, recipient_entity, cycle, count, amount
        from agg_contributions
        where
            contributor_type = 'I'
            and recipient_type = 'C'
            -- any transaction_type restrictions?
"""
            
            
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
    
