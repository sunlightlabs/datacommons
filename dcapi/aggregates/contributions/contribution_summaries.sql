
-- CONTRIBUTIONS FROM BIGGEST ORGS BY PARTY


select date_trunc('second', now()) || ' -- drop table if exists summary_party_from_biggest_org';
drop table if exists summary_party_from_biggest_org;

select date_trunc('second', now()) || ' -- create table summary_party_from_biggest_org';
create table summary_party_from_biggest_org as

        select
            organization_entity, name, recipient_party, cycle,
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party,cycle order by sum(amount) desc) as rank
        from
        (select
            organization_entity,
            me.name,
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            cycle,
            count,
            amount
        from
                matchbox_entity me
            inner join
                agg_party_from_org apfo on me.id = apfo.organization_entity
        where
            exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id)
            ) three_party
        group by organization_entity, name, recipient_party, cycle;

select date_trunc('second', now()) || ' -- Vcreate index summary_party_from_biggest_org_idx on summary_party_from_biggest_org (organization_entity, cycle)';
create index summary_party_from_biggest_org_idx on summary_party_from_biggest_org (organization_entity, recipient_party, cycle);

-- CONTRIBUTIONS FROM BIGGEST ORGS BY FEDERAL/STATE

select date_trunc('second', now()) || ' -- drop table if exists summary_namespace_from_biggest_org';
drop table if exists summary_namespace_from_biggest_org;

select date_trunc('second', now()) || ' -- create table summary_namespace_from_biggest_org';
create table summary_namespace_from_biggest_org as
        select
            organization_entity,
            me.name,
            transaction_namespace,
            cycle,
            count,
            amount,
            rank() over(partition by transaction_namespace,cycle order by amount desc) as rank
        from
                matchbox_entity me
            inner join
                agg_namespace_from_org apfo on me.id = apfo.organization_entity
        where
            exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);

select date_trunc('second', now()) || ' -- create index summary_namespace_from_biggest_org_idx on summary_namespace_from_biggest_org_org (organization_entity, cycle)';
create index summary_namespace_from_biggest_org_idx on summary_namespace_from_biggest_org (organization_entity, transaction_namespace, cycle);

-- CONTRIBUTIONS FROM BIGGEST ORGS BY SEAT

select date_trunc('second', now()) || ' -- drop table if exists summary_office_type_from_biggest_org';
drop table if exists summary_office_type_from_biggest_org;

select date_trunc('second', now()) || ' -- create table summary_office_type_from_biggest_org';
create table summary_office_type_from_biggest_org as
        select 
            organization_entity, 
            me.name, 
            seat,
            cycle, 
            count,
            amount, 
            rank() over(partition by seat,cycle order by amount desc) as rank 
        from 
                matchbox_entity me 
            inner join 
                agg_office_type_from_org apfo on me.id = apfo.organization_entity 
        where 
            exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
   
select date_trunc('second', now()) || ' -- create index summary_office_type_from_biggest_org_idx on summary_office_type_from_biggest_org_org (organization_entity, cycle)';
create index summary_office_type_from_biggest_org_idx on summary_office_type_from_biggest_org (organization_entity, seat, cycle);
