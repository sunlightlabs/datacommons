\set agg_top_n 10

select date_trunc('second', now()) || '-- Starting EPA aggregate computation...';

select date_trunc('second', now()) || '-- drop table epa_echo_org_map';
drop table if exists epa_echo_org_map cascade;

select date_trunc('second', now()) || '-- create table epa_echo_org_map';
create table epa_echo_org_map (
    case_ids text[],
    defendant_name varchar(255),
    org_name varchar(255),
    ultorg_name varchar(255)
);
select date_trunc('second', now()) || '-- Copying org_map from file';
\copy epa_echo_org_map from ~/work/epa/larrys_orgname_list.csv CSV HEADER


-- Associations Table

select date_trunc('second', now()) || '-- drop table assoc_epa_echo_org_ultorg';
drop table if exists assoc_epa_echo_org_ultorg cascade;

select date_trunc('second', now()) || '-- create table assoc_epa_echo_org_ultorg';
create table assoc_epa_echo_org_ultorg as
    select
        unnest(case_ids) as case_id,
        org.id as org_entity,
        ultorg.id as ultorg_entity
    from
        epa_echo_org_map m
        left join matchbox_entity org on lower(trim(both from m.org_name)) = lower(org.name)
        left join matchbox_entity ultorg on lower(trim(both from m.ultorg_name)) = lower(ultorg.name)
    where
        org.type = 'organization'
        and ultorg.type = 'organization'
;


-- Actions View

select date_trunc('second', now()) || '-- Dropping epa_echo_actions_view';
drop view epa_echo_actions_view;

select date_trunc('second', now()) || '-- Creating epa_echo_actions_view';
create view epa_echo_actions_view as
    select
        c.enfocnu as case_id,
        max(enfornm) as case_name,
        extract('year' from subacad)::integer + extract('year' from subacad)::integer % 2 as cycle,
        extract('year' from subacad)::integer as year,
        assoc.org_entity as defendant_entity,
        max(oe.name) as defendant_name,
        assoc.ultorg_entity as defendant_parent_entity,
        max(ue.name) as defendant_parent_name,
        subacty as date_significance,
        coalesce(enfotpa, 0) + coalesce(enfcslp, 0) + coalesce(enfcraa, 0) as amount
    from (select distinct on (enforcd) enfocnu, enfornm from epa_echo_case_identifier order by enforcd asc) c
    inner join epa_echo_penalty p on c.enfocnu = p.enfocnu
    inner join epa_echo_defendant d on c.enfocnu = d.enfocnu
    inner join (select distinct on (enfocnu) enfocnu, subacad, subacty from epa_echo_milestone order by enfocnu, subacad desc) m on m.enfocnu = c.enfocnu
    inner join assoc_epa_echo_org_ultorg assoc on assoc.case_id = c.enfocnu
    left join matchbox_entity oe on assoc.org_entity = oe.id
    left join matchbox_entity ue on assoc.ultorg_entity = ue.id
    group by assoc.org_entity, assoc.ultorg_entity, c.enfocnu, m.subacad, m.subacty, p.enfotpa, p.enfcslp, p.enfcraa
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
        from (select distinct on (defendant_entity, case_id) defendant_entity, cycle, amount from epa_echo_actions_view order by defendant_entity, case_id) x
        group by defendant_entity, cycle

        union all

        select
            defendant_parent_entity as entity_id,
            cycle,
            count(*) as count,
            sum(amount) as amount
        from epa_echo_actions_view
        group by defendant_parent_entity, cycle
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
            date_significance,
            rank() over (partition by defendant_entity, cycle order by max(amount) desc) as rank
        from epa_echo_actions_view
        group by cycle, year, defendant_entity, case_id, date_significance

        union all

        select
            cycle,
            year,
            defendant_parent_entity as defendant_entity,
            array_to_string(array_agg(defendant_name), ', ') as defendant_name,
            case_id,
            max(case_name) as case_name,
            max(amount) as amount,
            date_significance,
            rank() over (partition by defendant_parent_entity, cycle order by max(amount) desc) as rank
        from epa_echo_actions_view
        group by cycle, year, defendant_parent_entity, case_id, date_significance
    )

    select cycle, year, defendant_entity, defendant_name, case_id, case_name, amount, date_significance
    from actions_by_cycle
    where rank <= :agg_top_n

    union all

    select cycle, year, defendant_entity, defendant_name, case_id, case_name, amount, date_significance
    from (
        select -1 as cycle, year, defendant_entity, defendant_name, case_id, case_name, amount, date_significance,
            rank() over (partition by defendant_entity order by amount desc) as rank
        from actions_by_cycle
    ) x
    where rank <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (defendant_entity)';
create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (defendant_entity);


