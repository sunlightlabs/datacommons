\set agg_top_n 10

select date_trunc('second', now()) || '-- Starting EPA aggregate computation...';

select date_trunc('second', now()) || '-- Dropping associations table';
drop table if exists assoc_epa_echo cascade;

select date_trunc('second', now()) || '-- Creating associations table';
create table assoc_epa_echo as
    select
        e.id as entity_id,
        c.id as case_id,
        max(d.defennm) as defendant_name
    from epa_echo_case_identifier c
    inner join epa_echo_defendant d
        on d.enfocnu = c.enfocnu
    inner join matchbox_entity e
        on to_tsvector('datacommons', d.defennm) @@ plainto_tsquery('datacommons', e.name)
    where
        e.type = 'organization'
    group by
        e.id, c.id
;

select date_trunc('second', now()) || ' -- create index assoc_epa_echo_entity_id on assoc_epa_echo (entity_id)';
create index assoc_epa_echo_entity_id on assoc_epa_echo (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_epa_echo_case_id on assoc_epa_echo (case_id)';
create index assoc_epa_echo_case_id on assoc_epa_echo (case_id);


-- Actions View

select date_trunc('second', now()) || '-- Dropping epa_echo_actions_view';
drop view epa_echo_actions_view;

select date_trunc('second', now()) || '-- Creating epa_echo_actions_view';
create view epa_echo_actions_view as
    select
        extract('year' from max(subacad))::integer + extract('year' from max(subacad))::integer % 2 as cycle,
        extract('year' from max(subacad))::integer as year,
        assoc.entity_id as defendant_entity,
        max(defendant_name) as defendant_name,
        c.enfocnu as case_id,
        enfornm as case_name,
        coalesce(enfotpa, 0) + coalesce(enfcslp, 0) + coalesce(enfcraa, 0) as amount
    from epa_echo_case_identifier c
    inner join epa_echo_penalty p on c.enfocnu = p.enfocnu
    inner join epa_echo_milestone m on m.enfocnu = c.enfocnu
    inner join assoc_epa_echo assoc on assoc.case_id = c.id
    group by entity_id, c.enfocnu, enfornm, enfotpa, enfcslp, enfcraa
;



-- Totals

select date_trunc('second', now()) || '-- Dropping totals table';
drop table if exists agg_epa_echo_totals;

select date_trunc('second', now()) || '-- Creating totals table';

create table agg_epa_echo_totals as
    with cases_by_cycle as (
        select
            defendant_entity as entity_id,
            cycle,
            count(*) as count,
            sum(amount) as amount
        from epa_echo_actions_view
        group by defendant_entity, cycle
    )
    select entity_id, cycle, count, amount
    from cases_by_cycle

    union all

    select entity_id, -1 as cycle, sum(count) as count, sum(amount) as amount
    from cases_by_cycle
    group by entity_id
;
select date_trunc('second', now()) || ' -- create index agg_epa_echo_totals__entity_id on agg_epa_echo_totals (entity_id)';
create index agg_epa_echo_totals__entity_id on agg_epa_echo_totals (entity_id);


-- Top 10 Instances

select date_trunc('second', now()) || '-- Dropping aggregate table';
drop table if exists agg_epa_echo_actions;

select date_trunc('second', now()) || '-- Creating aggregate table';

create table agg_epa_echo_actions as
    with actions_by_cycle as (
        select
            cycle,
            year,
            defendant_entity,
            max(defendant_name) as defendant_name,
            case_id,
            max(case_name) as case_name,
            max(amount) as amount,
            rank() over (partition by defendant_entity, cycle order by max(amount) desc) as rank
        from epa_echo_actions_view
        group by cycle, year, defendant_entity, case_id
    )
    select cycle, year, defendant_entity, defendant_name, case_id, case_name, amount
    from actions_by_cycle
    where rank <= :agg_top_n

    union all

    select cycle, year, defendant_entity, defendant_name, case_id, case_name, amount
    from (
        select -1 as cycle, year, defendant_entity, defendant_name, case_id, case_name, amount,
            rank() over (partition by defendant_entity order by amount desc) as rank
        from actions_by_cycle
    ) x
    where rank <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (defendant_entity)';
create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (defendant_entity);


