\set agg_top_n 100
create table tmp_obama_for_bill as
    with org_contributions_by_cycle as (
        select
            recipient_entity, organization_name, organization_entity, cycle,
            coalesce(top_pacs.count, 0) as pacs_count,
            coalesce(top_pacs.amount, 0) as pacs_amount,
            rank() over (partition by recipient_entity, cycle order by coalesce(top_pacs.amount, 0) desc) as rank
        from (
            select ra.entity_id as recipient_entity, coalesce(oe.name, c.contributor_name) as organization_name,
                    ca.entity_id as organization_entity, cycle, count(*), sum(c.amount) as amount
                from contributions_organization c
                inner join recipient_associations ra using (transaction_id)
                left join contributor_associations ca using (transaction_id)
                left join matchbox_entity oe on oe.id = ca.entity_id
                where ra.entity_id = '4148b26f6f1c437cb50ea9ca4699417a'
                group by ra.entity_id, coalesce(oe.name, c.contributor_name), ca.entity_id, cycle
            ) top_pacs
    )
    select recipient_entity, organization_name, organization_entity, cycle, pacs_count, pacs_amount
    from org_contributions_by_cycle
    where rank <= :agg_top_n

    union all

    select recipient_entity, organization_name, organization_entity, -1, pacs_count, pacs_amount
    from (
        select
            recipient_entity, organization_name, organization_entity,
            sum(pacs_count) as pacs_count,
            sum(pacs_amount) as pacs_amount,
            rank() over (partition by recipient_entity order by sum(pacs_amount) desc) as rank
        from org_contributions_by_cycle
        group by recipient_entity, organization_name, organization_entity
    ) x
    where rank <= :agg_top_n;
