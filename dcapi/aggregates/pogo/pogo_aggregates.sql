\set latest_match_table matching_pogo_matches_20110523_1051
\set agg_top_n 10

select date_trunc('second', now()) || '-- Starting POGO aggregate computation...';

select date_trunc('second', now()) || '-- Dropping associations table';
drop table if exists assoc_pogo;

select date_trunc('second', now()) || '-- Creating associations table';
create table assoc_pogo as
    select distinct match_id::uuid as entity_id, misconduct.id::integer as misconduct_id
    from matching_pogo_matches_20110520_1717 matches
    inner join pogo_misconduct misconduct
    on subject_id = contractor_id
    where confidence > 2;

select date_trunc('second', now()) || ' -- create index assoc_pogo_entity_id on assoc_pogo (entity_id)';
create index assoc_pogo_entity_id on assoc_pogo (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_pogo_misconduct_id on assoc_pogo (misconduct_id)';
create index assoc_pogo_misconduct_id on assoc_pogo (misconduct_id);


-- Aggregate (top 10) table

select date_trunc('second', now()) || '-- Dropping aggregate table';
drop table if exists agg_pogo_contractor_misconduct;

select date_trunc('second', now()) || '-- Creating aggregate table';

create table agg_pogo_contractor_misconduct as
    with misconduct_by_cycle as (
        select
            date_year + date_year % 2 as cycle,
            date_year as year,
            entity.id as contractor_entity,
            contractor.name as contractor,
            contracting_party,
            penalty_amount,
            instance,
            court_type,
            misconduct_type,
            rank() over (partition by entity.id, date_year + date_year % 2 order by sum(penalty_amount) desc) as rank
        from pogo_misconduct misconduct
        inner join pogo_contractor contractor on misconduct.contractor_id = contractor.id
        inner join assoc_pogo assoc on assoc.misconduct_id = misconduct.id
        inner join matchbox_entity entity on assoc.entity_id = entity.id
        group by date_year, entity.id, contractor.name, contracting_party, penalty_amount, instance, court_type, misconduct_type
    )
    select cycle, year, contractor_entity, contractor, contracting_party, penalty_amount, instance, court_type, misconduct_type
    from misconduct_by_cycle
    where rank <= :agg_top_n

    union all

    select cycle, year, contractor_entity, contractor, contracting_party, penalty_amount, instance, court_type, misconduct_type
    from (
        select -1 as cycle, year, contractor_entity, contractor, contracting_party, penalty_amount, instance, court_type, misconduct_type,
            rank() over (partition by contractor_entity order by sum(penalty_amount) desc) as rank
        from misconduct_by_cycle
        group by year, contractor_entity, contractor, contracting_party, penalty_amount, instance, court_type, misconduct_type
    ) x
    where rank <= :agg_top_n
;


