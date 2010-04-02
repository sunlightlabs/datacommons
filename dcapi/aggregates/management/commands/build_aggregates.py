
from django.db import connection, transaction


create_contributor_assoc_stmt = """
    create table contributor_associations as
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
    create table recipient_associations as
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



create_agg_entities_stmt = """
    create table agg_entities as
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
 
 
 # just for use at the command line when setting up database
@transaction.commit_on_success
def setup_aggregates():
    transaction.set_dirty()
    cursor = connection.cursor()
    cursor.execute(create_contributor_assoc_stmt)
    cursor.execute(create_recipient_assoc_stmt)
    cursor.execute(create_agg_entities_stmt)
    cursor.execute(create_top_cat_to_cand_stmt)
    cursor.execute(create_top_cmtes_to_cand_stmt)
    cursor.execute(create_top_indiv_to_cand_stmt)
    cursor.execute(create_top_indiv_to_cmte_stmt)
   