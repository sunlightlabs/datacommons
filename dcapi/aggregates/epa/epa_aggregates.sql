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
\copy epa_echo_org_map from larrys_orgname_list.csv CSV HEADER


-- relevant actions
-- NOTE: This table needs to exactly match the model definition so that the TransparencyData search code can access it

drop view if exists epa_echo_relevant_actions;

drop table if exists epa_echo_actions cascade;

create table epa_echo_actions as
select i.enfocnu as case_num, max(enfornm) as case_name,
    (select min(subacad) from epa_echo_milestone m where m.enfocnu = i.enfocnu) as first_date,
    (select max(subacad) from epa_echo_milestone m where m.enfocnu = i.enfocnu) as last_date,
    (select subacty from epa_echo_milestone m where m.enfocnu = i.enfocnu order by subacad limit 1) as first_date_significance,
    (select subacty from epa_echo_milestone m where m.enfocnu = i.enfocnu order by subacad desc limit 1) as last_date_significance,
    (select sum(coalesce(enfccaa, 0) + coalesce(enfcraa, 0) + coalesce(enfotpa, 0) + coalesce(enfotsa, 0)) from epa_echo_penalty p where p.enfocnu = i.enfocnu) as penalty,
    (select sum(coalesce(enfops, 0)) from epa_echo_penalty p where p.enfocnu = i.enfocnu) as penalty_enfops,
    (select sum(coalesce(enfccaa, 0)) from epa_echo_penalty p where p.enfocnu = i.enfocnu) as penalty_enfccaa,
    (select sum(coalesce(enfcraa, 0)) from epa_echo_penalty p where p.enfocnu = i.enfocnu) as penalty_enfcraa,
    (select sum(coalesce(enfotpa, 0)) from epa_echo_penalty p where p.enfocnu = i.enfocnu) as penalty_enfotpa,
    (select sum(coalesce(enfotsa, 0)) from epa_echo_penalty p where p.enfocnu = i.enfocnu) as penalty_enfotsa,
    (select count(distinct defennm) from epa_echo_defendant d where d.enfocnu = i.enfocnu) as num_defendants,
    (select array_to_string(array_agg(distinct d.defennm), ', ') from epa_echo_defendant d where d.enfocnu = i.enfocnu) as defendants,
    (select array_to_string(array_agg(distinct f.fcltcit || ', ' || f.fcltstc), '; ') from epa_echo_facility f where f.enfocnu = i.enfocnu) as locations,
    (select array_to_string(array_agg(distinct f.fcltyad || ', ' || f.fcltcit || ', ' || f.fcltstc), '; ') from epa_echo_facility f where f.enfocnu = i.enfocnu) as location_addresses
from epa_echo_case_identifier i
group by i.enfocnu;

create index epa_echo_actions_case_num_idx on epa_echo_actions (case_num);
create index epa_echo_actions_case_name_idx on epa_echo_actions using gin(to_tsvector('datacommons', case_name));
create index epa_echo_actions_defendants_idx on epa_echo_actions using gin(to_tsvector('datacommons', defendants));
create index epa_echo_actions_locations_idx on epa_echo_actions using gin(to_tsvector('datacommons', locations));
create index epa_echo_actions_penalty_idx on epa_echo_actions (penalty);


create view epa_echo_relevant_actions as
    select *, extract('year' from last_date)::integer + extract('year' from last_date)::integer % 2 as cycle
    from epa_echo_actions
    where
        extract('year' from first_date) > 2000
        and penalty > 1000000;


-- Associations Table

select date_trunc('second', now()) || '-- drop table assoc_epa_echo_org_ultorg';
drop table if exists assoc_epa_echo_org cascade;

select date_trunc('second', now()) || '-- create table assoc_epa_echo_org_ultorg';
create table assoc_epa_echo_org as
    select d.enfocnu as case_num, max(d.defennm) as defendant_name, e.id as entity_id
    from epa_echo_relevant_actions a
    inner join epa_echo_defendant d on d.enfocnu = a.case_num
    inner join epa_echo_org_map m on d.defennm = m.defendant_name
    inner join matchbox_entity e on e.name = m.org_name or e.name = m.ultorg_name
    group by d.enfocnu, e.id;


-- Totals

select date_trunc('second', now()) || '-- Dropping totals table';
drop table if exists agg_epa_echo_totals;

select date_trunc('second', now()) || '-- Creating totals table';

create table agg_epa_echo_totals as
    with cases_by_cycle as (
        select
            entity_id,
            cycle,
            count(*),
            sum(penalty) as amount
        from epa_echo_relevant_actions a
        inner join assoc_epa_echo_org o using (case_num)
        group by entity_id, cycle
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
            a.*,
            o.defendant_name,
            o.entity_id,
            rank() over (partition by entity_id, cycle order by case when num_defendants = 1 then penalty else -1.0 / penalty end desc) as rank
        from epa_echo_relevant_actions a
        inner join assoc_epa_echo_org o using (case_num)
    )

    select cycle, case_num, case_name, defendant_name, entity_id, num_defendants, defendants, locations, location_addresses,
        penalty, extract('year' from last_date)::integer as year, last_date_significance,
        rank
    from actions_by_cycle
    where rank <= :agg_top_n

    union all

    select *
    from (
        select -1 as cycle, case_num, case_name, defendant_name, entity_id, num_defendants, defendants, locations, location_addresses,
            penalty, extract('year' from last_date)::integer as year, last_date_significance,
            rank() over (partition by entity_id order by case when num_defendants = 1 then penalty else -1.0 / penalty end desc) as rank
        from actions_by_cycle
    ) x
    where x.rank <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (defendant_entity)';
create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (entity_id);


