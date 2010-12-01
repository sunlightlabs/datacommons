-- Member associations

select date_trunc('second', now()) || ' -- drop table if exists earmarks_member_associations';
drop table if exists earmarks_member_associations;

select date_trunc('second', now()) || ' -- create table earmarks_member_associations';
create table earmarks_member_associations as
    select
        ea.entity_id,
        m.earmark_id
    from earmarks_member m
    inner join matchbox_entityattribute ea
        on m.crp_id = ea.value
    where
        ea.namespace = 'urn:crp:recipient'
    ;

select date_trunc('second', now()) || ' -- create index earmarks_member_associations_entity_id on earmarks_member_associations (entity_id)';
create index earmarks_member_associations_entity_id on earmarks_member_associations (entity_id);
select date_trunc('second', now()) || ' -- create index earmarks_member_associations_earmark_id on earmarks_member_associations (earmark_id)';
create index earmarks_member_associations_earmark_id on earmarks_member_associations (earmark_id);


-- Recipient Associations

select date_trunc('second', now()) || ' -- drop table if exists earmarks_recipient_associations';
drop table if exists earmarks_recipient_associations;

select date_trunc('second', now()) || ' -- create table earmarks_recipient_associations';
create table earmarks_recipient_associations as
    select
        e.id as entity_id,
        r.earmark_id
    from earmarks_recipient r
    inner join matchbox_entity e
        on e.name = r.standardized_recipient
    where
        e.type = 'organization'
    ;

select date_trunc('second', now()) || ' -- create index earmarks_recipient_associations_entity_id on earmarks_recipient_associations (entity_id)';
create index earmarks_recipient_associations_entity_id on earmarks_recipient_associations (entity_id);
select date_trunc('second', now()) || ' -- create index earmarks_recipient_associations_earmark_id on earmarks_recipient_associations (earmark_id)';
create index earmarks_recipient_associations_earmark_id on earmarks_recipient_associations (earmark_id);

-- Earmark Totals

select date_trunc('second', now()) || ' -- drop table if exists agg_earmark_totals';
drop table if exists agg_earmark_totals;

select date_trunc('second', now()) || ' -- create table agg_earmark_totals';
create table agg_earmark_totals as
    with earmarks_by_entity_cycle as (
        select
            coalesce(ma.entity_id, ra.entity_id) as entity_id,
            case when fiscal_year % 2 = 0 then fiscal_year else fiscal_year + 1 end as cycle,
            count(*) as count,
            sum(final_amount) as amount
        from
            earmarks_earmark e
            left join earmarks_member_associations ma on e.id = ma.earmark_id
            left join earmarks_recipient_associations ra on e.id = ra.earmark_id
        group by
            coalesce(ma.entity_id, ra.entity_id),
            case when fiscal_year % 2 = 0 then fiscal_year else fiscal_year + 1 end
    )
    select entity_id, cycle, count, amount
    from earmarks_by_entity_cycle

    union all

    select entity_id, -1, sum(count) as count, sum(amount) as amount
    from earmarks_by_entity_cycle
    group by entity_id
;

select date_trunc('second', now()) || ' -- create index agg_earmark_totals_entity_id on agg_earmark_totals (entity_id)';
create index agg_earmark_totals_entity_id on agg_earmark_totals (entity_id);
select date_trunc('second', now()) || ' -- create index agg_earmark_totals_cycle on agg_earmark_totals (cycle)';
create index agg_earmark_totals_cycle on agg_earmark_totals (cycle);

select date_trunc('second', now()) || ' -- Finished computing earmark aggregates.';
