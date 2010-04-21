-- Cycles: controls the cycles for which aggregates are computed
-- Mainly of using during development, when it helps to be able to regenerate the aggregates quickly.

drop table if exists agg_cycles cascade;

create table agg_cycles as
--    values (2005), (2006), (2007), (2008), (2009), (2010);
    select distinct cycle from contribution_contribution;

-- Top N: the number of rows to generate for each aggregate

--\set agg_top_n 10
\set agg_top_n 100


-- CatCodes that should not be included in totals.
-- Taken from the NIMSP column CatCodes.TopSuppress.

drop table if exists agg_suppressed_catcodes;

create table agg_suppressed_catcodes as
    values ('Z2100'), ('Z2200'), ('Z2300'), ('Z2400'), ('Z7777'), ('Z8888'), ('Z9100'), ('Z9500'), ('Z9600'), ('Z9700'), ('Z9999');


-- Only contributions that should be included in totals from individuals

drop view if exists contributions_individual;

create view contributions_individual as
    select *
    from contribution_contribution c
    where
        (c.contributor_type is null or c.contributor_type in ('', 'I'))
        and c.recipient_type = 'P'
        and c.transaction_type in ('', '11', '15', '15e', '15j', '22y')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);
    

-- Only contributions that should be included in totals from organizations

drop view if exists contributions_organization;

create view contributions_organization as
    select *
    from contribution_contribution c
    where
        contributor_type = 'C'
        and recipient_type = 'P'
        and transaction_type in ('', '24k', '24r', '24z')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);
    

-- Contributor Associations

drop table if exists contributor_associations;

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
        and ((a.namespace in ('urn:crp:individual', 'urn:crp:organization') and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace in ('urn:nimsp:individual', 'urn:nimsp:organization') and c.transaction_namespace = 'urn:nimsp:transaction'));

create index contributor_associations_entity_id on contributor_associations (entity_id);
create index contributor_associations_transaction_id on contributor_associations (transaction_id);  


-- Organization Associations

drop table if exists organization_associations;

create table organization_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on c.organization_name = a.alias
    where
        a.verified = 't'
union
    select a.entity_id, c.transaction_id
        from contribution_contribution c
        inner join matchbox_entityalias a
            on c.parent_organization_name = a.alias
        where
            a.verified = 't'
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.organization_ext_id = a.value
    where
        a.verified = 't'
        and ((a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'))
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.parent_organization_ext_id = a.value
    where
        a.verified = 't'
        and ((a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'));
            
create index organization_associations_entity_id on organization_associations (entity_id);
create index organization_associations_transaction_id on organization_associations (transaction_id);
    

-- Recipient Associations

drop table if exists recipient_associations;

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
            or (a.namespace = 'urn:nimsp:recipient' and c.transaction_namespace = 'urn:nimsp:transaction'));


create index recipient_associations_entity_id on recipient_associations (entity_id);
create index recipient_associations_transaction_id on recipient_associations (transaction_id);             


-- Entity Aggregates

drop table if exists agg_entities;

create table agg_entities as
    select entity_id, -1 as cycle, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count, 
        coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
    from 
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from (select * from contributor_associations union select * from organization_associations) a
        inner join contribution_contribution transaction using (transaction_id)
        group by a.entity_id) as contrib_aggs
    full outer join
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from recipient_associations a
        inner join contribution_contribution transaction using (transaction_id)
        group by a.entity_id) as recip_aggs
    using (entity_id)
union
    select entity_id, coalesce(contrib_aggs.cycle, recip_aggs.cycle) as cycle, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count, 
        coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
    from
        (select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
        from (select * from contributor_associations union select * from organization_associations) a
        inner join contribution_contribution transaction using (transaction_id)
        group by a.entity_id, transaction.cycle) as contrib_aggs
    full outer join
        (select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
        from recipient_associations a
        inner join contribution_contribution transaction using (transaction_id)
        group by a.entity_id, transaction.cycle) as recip_aggs
    using (entity_id, cycle);
        
create index agg_entities_entity_id on agg_entities (entity_id);


-- Industry Sector to Candidate

drop table if exists agg_sectors_to_cand_by_cycle;

create table agg_sectors_to_cand_by_cycle as
    select top.recipient_entity, top.sector, top.cycle, top.count, top.amount 
    from
        (select ra.entity_id as recipient_entity, substring(c.contributor_category_order for 1) as sector, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, substring(c.contributor_category_order for 1), c.cycle) top
    where
        rank <= :agg_top_n;
        
create index agg_sectors_to_cand_by_cycle_recipient_entity on agg_sectors_to_cand_by_cycle (recipient_entity);
       
       
-- Industry Category Orders to Candidate

drop table if exists agg_cat_orders_to_cand_by_cycle;

create table agg_cat_orders_to_cand_by_cycle as
    select top.recipient_entity, top.sector, top.contributor_category_order, top.cycle, top.count, top.amount 
    from
        (select ra.entity_id as recipient_entity, substring(c.contributor_category_order for 1) as sector, c.contributor_category_order, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, substring(c.contributor_category_order for 1), c.cycle order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, substring(c.contributor_category_order for 1), c.contributor_category_order, c.cycle) top
    where
        rank <= :agg_top_n;

create index agg_cat_orders_to_cand_by_cycle_recipient_entity on agg_cat_orders_to_cand_by_cycle (recipient_entity);
        
        
-- Candidates from Individual

drop table if exists agg_cands_from_indiv_by_cycle;

create table agg_cands_from_indiv_by_cycle as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity, 
            cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= :agg_top_n;

create index agg_cands_from_indiv_by_cycle_contributor_entity on agg_cands_from_indiv_by_cycle (contributor_entity);
    
    
-- Committees from Individual

drop table if exists agg_cmtes_from_indiv_by_cycle;

create table agg_cmtes_from_indiv_by_cycle as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual c
        inner join contributor_associations ca using(transaction_id)
        left join recipient_associations ra using (transaction_id)
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= :agg_top_n;
        
create index agg_cmtes_from_indiv_by_cycle_contributor_entity on agg_cmtes_from_indiv_by_cycle (contributor_entity);
    
    
-- Candidates from Committee

drop table if exists agg_cands_from_cmte_by_cycle;

create table agg_cands_from_cmte_by_cycle as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity, 
            cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_organization c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= :agg_top_n;

create index agg_cands_from_cmte_by_cycle_contributor_entity on agg_cands_from_cmte_by_cycle (contributor_entity);


-- Individuals to Committee

drop table if exists agg_indivs_to_cmte_by_cycle;

create table agg_indivs_to_cmte_by_cycle as
    select top.recipient_entity, top.contributor_name, top.contributor_entity, top.cycle, top.count, top.amount
    from (select ra.entity_id as recipient_entity, c.contributor_name, coalesce(ca.entity_id, '') as contributor_entity, 
            cycle, count(*), sum(c.amount) as amount, 
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from contribution_contribution c
        inner join recipient_associations ra using (transaction_id)
        left join contributor_associations ca using (transaction_id)
        where
            (c.contributor_type is null or c.contributor_type in ('', 'I'))
            and c.recipient_type = 'C'
            -- any type restrictions?
            and cycle in (select * from agg_cycles)
        group by ra.entity_id, c.contributor_name, coalesce(ca.entity_id, ''), cycle) top
    where
        rank <= :agg_top_n;

create index agg_indivs_to_cmte_by_cycle_recipient_entity on agg_indivs_to_cmte_by_cycle (recipient_entity);


-- Organizations to Candidate

drop table if exists agg_orgs_to_cand_by_cycle;

create table agg_orgs_to_cand_by_cycle as
    select  top.recipient_entity, top.organization_name, top.organization_entity, top.cycle, 
            top.total_count, top.pacs_count, top.indivs_count, top.total_amount, top.pacs_amount, top.indivs_amount
    from   
        (select recipient_entity, organization_name, organization_entity, cycle,
            coalesce(top_pacs.count, 0) + coalesce(top_indivs.count, 0) as total_count, coalesce(top_pacs.count, 0) as pacs_count, coalesce(top_indivs.count, 0) as indivs_count,
            coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0) as total_amount, coalesce(top_pacs.amount, 0) as pacs_amount, coalesce(top_indivs.amount, 0) as indivs_amount,
            rank() over (partition by recipient_entity, cycle order by (coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0)) desc) as rank
        from
                (select ra.entity_id as recipient_entity, c.contributor_name as organization_name, coalesce(ca.entity_id, '') as organization_entity, 
                    cycle, count(*), sum(c.amount) as amount 
                from contributions_organization c
                inner join recipient_associations ra using (transaction_id)
                left join contributor_associations ca using (transaction_id)
                group by ra.entity_id, c.contributor_name, coalesce(ca.entity_id, ''), cycle) top_pacs
            full outer join
                (select ra.entity_id as recipient_entity, 
                    case when parent_organization_name != '' then parent_organization_name
                        else organization_name end as organization_name,
                    coalesce(oa.entity_id, '') as organization_entity,
                    cycle, count(*) as count, sum(amount) as amount
                from contributions_individual c
                inner join recipient_associations ra using (transaction_id)
                left join organization_associations oa using (transaction_id)
                where
                    organization_name != '' or parent_organization_name != ''
                group by ra.entity_id,
                    case when parent_organization_name != '' then parent_organization_name
                        else organization_name end,
                    coalesce(oa.entity_id, ''), cycle) top_indivs
        using (recipient_entity, organization_name, organization_entity, cycle)) top
    where
        rank <= :agg_top_n;
        
create index agg_orgs_to_cand_by_cycle_recipient_entity on agg_orgs_to_cand_by_cycle (recipient_entity);
    
    
-- Candidates from Organization

drop table if exists agg_cands_from_org_by_cycle;

create table agg_cands_from_org_by_cycle as
    select  top.organization_entity, top.recipient_name, top.recipient_entity, top.cycle, 
            top.total_count, top.pacs_count, top.indivs_count, top.total_amount, top.pacs_amount, top.indivs_amount
    from   
        (select organization_entity, recipient_name, recipient_entity, cycle,
            coalesce(top_direct.count, 0) + coalesce(top_indivs.count, 0) as total_count, coalesce(top_direct.count, 0) as pacs_count, coalesce(top_indivs.count, 0) as indivs_count,
            coalesce(top_direct.amount, 0) + coalesce(top_indivs.amount, 0) as total_amount, coalesce(top_direct.amount, 0) as pacs_amount, coalesce(top_indivs.amount, 0) as indivs_amount,
            rank() over (partition by organization_entity, cycle order by (coalesce(top_direct.amount, 0) + coalesce(top_indivs.amount, 0)) desc) as rank
        from
                (select ca.entity_id as organization_entity, c.recipient_name as recipient_name, coalesce(ra.entity_id, '') as recipient_entity, 
                    cycle, count(*), sum(c.amount) as amount 
                from contributions_organization c
                inner join contributor_associations ca using (transaction_id)
                left join recipient_associations ra using (transaction_id)
                group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top_direct
            full outer join
                (select oa.entity_id as organization_entity, c.recipient_name as recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
                    cycle, count(*), sum(amount) as amount
                from contributions_individual c
                inner join organization_associations oa using (transaction_id)
                left join recipient_associations ra using (transaction_id)
                group by oa.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top_indivs
            using (organization_entity, recipient_name, recipient_entity, cycle)) top
    where
        rank <= :agg_top_n;

create index agg_cands_from_org_by_cycle_organization_entity on agg_cands_from_org_by_cycle (organization_entity);
  
    
-- Party from Individual

drop table if exists agg_party_from_indiv_by_cycle;

create table agg_party_from_indiv_by_cycle as
    select ca.entity_id as contributor_entity, c.cycle, c.recipient_party, count(*), sum(c.amount) as amount
    from contributions_individual c
    inner join contributor_associations ca using (transaction_id)
    group by ca.entity_id, c.cycle, c.recipient_party;
    
create index agg_party_from_indiv_by_cycle_contributor_entity on agg_party_from_indiv_by_cycle (contributor_entity);
    
    
-- Party from Organization

drop table if exists agg_party_from_org_by_cycle;

create table agg_party_from_org_by_cycle as
    select oa.entity_id as organization_entity, c.cycle, c.recipient_party, count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join organization_associations oa using (transaction_id)
    group by oa.entity_id, c.cycle, c.recipient_party;

create index agg_party_from_org_by_cycle_organization_entity on agg_party_from_org_by_cycle (organization_entity);
    
    
-- State/Fed from Organization

drop table if exists agg_namespace_from_org_by_cycle;

create table agg_namespace_from_org_by_cycle as
    select oa.entity_id as organization_entity, c.cycle, c.transaction_namespace, count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join organization_associations oa using (transaction_id)
    group by oa.entity_id, c.cycle, c.transaction_namespace;
    
create index agg_namespace_from_org_by_cycle_organization_entity on agg_namespace_from_org_by_cycle (organization_entity);
    
    
-- In-state/Out-of-state to Politician

drop table if exists agg_local_to_politician_by_cycle;

create table agg_local_to_politician_by_cycle as
    select ra.entity_id as recipient_entity, c.cycle, 
        case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end as local,
        count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, c.cycle, case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end;
    
create index agg_local_to_politician_by_cycle_recipient_entity on agg_local_to_politician_by_cycle (recipient_entity);
    
    
-- Indiv/PAC to Politician

drop table if exists agg_contributor_type_to_politician_by_cycle;

create table agg_contributor_type_to_politician_by_cycle as
    select ra.entity_id as recipient_entity, c.cycle, coalesce(c.contributor_type, '') as contributor_type, count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, c.cycle, coalesce(c.contributor_type, '');
    
create index agg_contributor_type_to_politician_by_cycle_recipient_entity on agg_contributor_type_to_politician_by_cycle (recipient_entity);


    