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

drop table if exists epa_echo_actions cascade;

create table epa_echo_actions as
select i.enfocnu as case_num, max(enfornm) as case_name,
    extract('year' from (select min(subacad) from epa_echo_milestone m where m.enfocnu = i.enfocnu))::integer as min_year,
    extract('year' from (select max(subacad) from epa_echo_milestone m where m.enfocnu = i.enfocnu))::integer as max_year,
    (select count(*) from epa_echo_defendant d where d.enfocnu = i.enfocnu) as num_defendants,
    'to do'::varchar(255) as max_year_significance,
    (select sum(coalesce(enfccaa, 0) + coalesce(enfcraa, 0) + coalesce(enfotpa, 0) + coalesce(enfotsa, 0)) from epa_echo_penalty p where p.enfocnu = i.enfocnu) as penalty
from epa_echo_case_identifier i
group by i.enfocnu;


drop view if exists epa_echo_relevant_actions;

create view epa_echo_relevant_actions as
    select *, max_year + max_year % 2 as cycle
    from epa_echo_actions
    where
        min_year > 2000
        and penalty > 1000000;


-- Associations Table

select date_trunc('second', now()) || '-- drop table assoc_epa_echo_org_ultorg';
drop table if exists assoc_epa_echo_org cascade;

select date_trunc('second', now()) || '-- create table assoc_epa_echo_org_ultorg';
create table assoc_epa_echo_org as
    select d.enfocnu as case_num, e.id as entity_id
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
            o.entity_id,
            rank() over (partition by entity_id, cycle order by penalty desc) as rank
        from epa_echo_relevant_actions a
        inner join assoc_epa_echo_org o using (case_num)
    )

    select cycle, max_year, entity_id, case_num, case_name, penalty, max_year_significance
    from actions_by_cycle
    where rank <= :agg_top_n

    union all

    select cycle, max_year, entity_id, case_num, case_name, penalty, max_year_significance
    from (
        select -1 as cycle, max_year, entity_id, case_num, case_name, penalty, max_year_significance,
            rank() over (partition by entity_id order by penalty desc) as rank
        from actions_by_cycle
    ) x
    where rank <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (defendant_entity)';
create index agg_epa_echo_actions__defendant_entity on agg_epa_echo_actions (entity_id);


