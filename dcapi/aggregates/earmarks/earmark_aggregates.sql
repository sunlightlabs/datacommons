-- Top N: the number of rows to generate for each aggregate

\set agg_top_n 10

-- Earmarks Normalized to Cycles

select date_trunc('second', now()) || ' -- drop view if exists earmarks_by_cycle';
drop view if exists earmarks_by_cycle;

select date_trunc('second', now()) || ' -- create view earmarks_by_cycle';
create view earmarks_by_cycle as
    select
        *,
        case when fiscal_year % 2 = 0 then fiscal_year else fiscal_year - 1 end as cycle
    from
        earmarks_earmark
    where
        presidential = '' -- don't include any sort of presidential earmark
;

-- Member Associations

select date_trunc('second', now()) || ' -- drop table if exists assoc_earmarks_member';
drop table if exists assoc_earmarks_member;

select date_trunc('second', now()) || ' -- create table assoc_earmarks_member';
create table assoc_earmarks_member as
    select
        ea.entity_id,
        m.id as member_id,
        m.earmark_id
    from earmarks_member m
    inner join matchbox_entityattribute ea
        on m.crp_id = ea.value
    where
        ea.namespace = 'urn:crp:recipient'
;

select date_trunc('second', now()) || ' -- create index assoc_earmarks_member_entity_id on assoc_earmarks_member (entity_id)';
create index assoc_earmarks_member_entity_id on assoc_earmarks_member (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_earmarks_member_earmark_id on assoc_earmarks_member (earmark_id)';
create index assoc_earmarks_member_earmark_id on assoc_earmarks_member (earmark_id);


-- Recipient Associations

select date_trunc('second', now()) || ' -- drop table if exists assoc_earmarks_recipient';
drop table if exists assoc_earmarks_recipient;

select date_trunc('second', now()) || ' -- create table assoc_earmarks_recipient';
create table assoc_earmarks_recipient as
    select
        e.id as entity_id,
        r.id as recipient_id,
        r.earmark_id
    from earmarks_recipient r
    inner join matchbox_entity e
        on e.name = r.standardized_recipient
    where
        e.type = 'organization'
    ;

select date_trunc('second', now()) || ' -- create index assoc_earmarks_recipient_entity_id on assoc_earmarks_recipient (entity_id)';
create index assoc_earmarks_recipient_entity_id on assoc_earmarks_recipient (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_earmarks_recipient_earmark_id on assoc_earmarks_recipient (earmark_id)';
create index assoc_earmarks_recipient_earmark_id on assoc_earmarks_recipient (earmark_id);


-- Flattened earmarks

select date_trunc('second', now()) || ' -- drop table if exists earmarks_flattened';
drop table if exists earmarks_flattened;

select date_trunc('second', now()) || ' -- create table earmarks_flattened';
create table earmarks_flattened as
    select
        e.id,
        cycle,
        fiscal_year,
        final_amount,
        description,
        ARRAY(
            select '{"name":"' || standardized_name || '", "id":"' || replace(coalesce(a.entity_id::varchar, ''), '-', '') || '"}'
            from earmarks_member m
            left join assoc_earmarks_member a
                on m.id = a.member_id
            where
                e.id = m.earmark_id
            ) as members,
        ARRAY(
            select '{"name":"' || case when standardized_recipient != '' then standardized_recipient else raw_recipient end || '", "id":"' || replace(coalesce(a.entity_id::varchar, ''), '-', '') || '"}'
            from earmarks_recipient r
            left join assoc_earmarks_recipient a
                on r.id = a.recipient_id
            where
                e.id = r.earmark_id
            ) as recipients
    from
        earmarks_by_cycle e;





-- Member with Our Metadata If Matched, Data from Earmark If Not

select date_trunc('second', now()) || ' -- drop table if exists earmarks_member_w_metadata';
drop table if exists earmarks_member_w_metadata;

select date_trunc('second', now()) || ' -- create table earmarks_member_w_metadata';
create table earmarks_member_w_metadata as
    select
        m.earmark_id,
        m.id as member_id,
        entity_id,
        standardized_name as name,
        coalesce(meta.state, m.state) as state,
        coalesce(meta.seat, m.chamber) as seat, -- needs more work to convert to same format, but currently unneeded
        coalesce(meta.party, m.party) as party
    from
        earmarks_member m
        left join assoc_earmarks_member ma
            on m.id = ma.member_id
        left join politician_metadata_latest_cycle_view meta using (entity_id)
;

select date_trunc('second', now()) || ' -- create index earmarks_member_w_metadata_entity_id on earmarks_member_w_metadata (entity_id)';
create index earmarks_member_w_metadata_entity_id on earmarks_member_w_metadata (entity_id);

-- Earmark Totals

select date_trunc('second', now()) || ' -- drop table if exists agg_earmark_totals';
drop table if exists agg_earmark_totals;

select date_trunc('second', now()) || ' -- create table agg_earmark_totals';
create table agg_earmark_totals as
    with earmarks_by_entity_cycle as (
        select
            ma.entity_id as entity_id,
            cycle,
            count(*) as count,
            sum(final_amount) as amount
        from
            earmarks_by_cycle e
            inner join assoc_earmarks_member ma on e.id = ma.earmark_id
        group by
            ma.entity_id,
            cycle

        union all

        select
            ra.entity_id as entity_id,
            cycle,
            count(*) as count,
            sum(final_amount) as amount
        from
            earmarks_by_cycle e
            inner join assoc_earmarks_recipient ra on e.id = ra.earmark_id
        group by
            ra.entity_id,
            cycle
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



-- Top 10 Earmarks by Amount per Entity

select date_trunc('second', now()) || ' -- drop table if exists agg_earmarks_by_amt_per_entity';
drop table if exists agg_earmarks_by_amt_per_entity;

select date_trunc('second', now()) || ' -- create table agg_earmarks_by_amt_per_entity';
create table agg_earmarks_by_amt_per_entity as
    with earmarks_by_entity_cycle as (
        select
            e.id as earmark_id,
            cycle,
            fiscal_year,
            ma.entity_id as entity_id,
            final_amount as amount,
            description,
            members,
            recipients,
            rank() over (partition by ma.entity_id, cycle order by final_amount desc) as rank
        from
            earmarks_flattened e
            inner join assoc_earmarks_member ma on e.id = ma.earmark_id

        union all

        select
            e.id as earmark_id,
            cycle,
            fiscal_year,
            ra.entity_id as entity_id,
            final_amount as amount,
            description,
            members,
            recipients,
            rank() over (partition by ra.entity_id, cycle order by final_amount desc) as rank
        from
            earmarks_flattened e
            inner join assoc_earmarks_recipient ra on e.id = ra.earmark_id
    )

    select earmark_id, cycle, fiscal_year, entity_id, amount, description, members, recipients
    from earmarks_by_entity_cycle
    where rank <= :agg_top_n

    union all

    select earmark_id, -1, fiscal_year, entity_id, amount, description, members, recipients
    from (
        select earmark_id, fiscal_year, entity_id, amount, description, members, recipients, rank() over (partition by entity_id order by amount desc) as rank
        from earmarks_by_entity_cycle
    )x
    where rank <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index agg_earmarks_by_amt_per_entity_idx';
create index agg_earmarks_by_amt_per_entity_idx on agg_earmarks_by_amt_per_entity (entity_id, cycle);



-- Amount Earmarked In-State vs Out-State Per Member

select date_trunc('second', now()) || ' -- drop table if exists agg_earmark_amt_by_entity_in_state_out_state';
drop table if exists agg_earmark_amt_by_entity_in_state_out_state;

select date_trunc('second', now()) || ' -- create table agg_earmark_amt_by_entity_in_state_out_state';
create table agg_earmark_amt_by_entity_in_state_out_state as
    with local_per_earmark as (
        select
            meta.entity_id,
            cycle,
            case
                when not exists (select * from earmarks_location l where l.earmark_id = e.id) then 'unknown'
                when exists (select * from earmarks_location l where l.earmark_id = e.id and l.state = meta.state) then 'in-state'
                else 'out-of-state'
            end as local,
            final_amount
        from
            earmarks_by_cycle e
            inner join earmarks_member_w_metadata meta
                on e.id = meta.earmark_id
    )

    select entity_id, cycle, local, count(*) as count, sum(final_amount) as amount
    from local_per_earmark
    group by entity_id, cycle, local

    union all

    select entity_id, -1, local, count(*) as count, sum(final_amount) as amount
    from local_per_earmark
    group by entity_id, local
;

select date_trunc('second', now()) || ' -- create index agg_earmark_amt_by_entity_in_state_out_state_idx';
create index agg_earmark_amt_by_entity_in_state_out_state_idx on agg_earmark_amt_by_entity_in_state_out_state (entity_id, cycle);


-- The End

select date_trunc('second', now()) || ' -- Finished computing earmark aggregates.';
