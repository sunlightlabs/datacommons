-- Cycles: controls the cycles for which aggregates are computed
-- Mainly of using during development, when it helps to be able to regenerate the aggregates quickly.

select date_trunc('second', now()) || ' -- Starting contribution aggregate computation...';

select date_trunc('second', now()) || ' -- drop table if exists agg_cycles cascade';
drop table if exists agg_cycles cascade;

select date_trunc('second', now()) || ' -- create table agg_cycles';
create table agg_cycles as
--    values (2005), (2006), (2007), (2008), (2009), (2010);
    select distinct cycle from contribution_contribution;


-- Top N: the number of rows to generate for each aggregate

\set agg_top_n 10


-- CatCodes that should not be included in totals.
-- Taken from the NIMSP column CatCodes.TopSuppress.


select date_trunc('second', now()) || ' -- drop table if exists agg_suppressed_catcodes';
drop table if exists agg_suppressed_catcodes;

select date_trunc('second', now()) || ' -- create table agg_suppressed_catcodes';
create table agg_suppressed_catcodes as
    values ('Z2100'), ('Z2200'), ('Z2300'), ('Z2400'), ('Z7777'), ('Z8888'),
        ('Z9010'), ('Z9020'), ('Z9030'), ('Z9040'),
        ('Z9100'), ('Z9500'), ('Z9600'), ('Z9700'), ('Z9999');



-- Adjust the odd-year cycles upward


select date_trunc('second', now()) || ' -- drop view if exists contributions_even_cycles cascade';
drop view if exists contributions_even_cycles cascade;

select date_trunc('second', now()) || ' -- create view contributions_even_cycles';
create view contributions_even_cycles as
    select transaction_id, transaction_namespace, transaction_type, amount,
        case when cycle % 2 = 0 then cycle else cycle + 1 end as cycle, date,
        contributor_name, contributor_type, contributor_category, contributor_state,
        organization_name, parent_organization_name,
        recipient_name, recipient_type, recipient_party, recipient_state, recipient_category
    from contribution_contribution;



-- Only contributions that should be included in totals from individuals to politicians


select date_trunc('second', now()) || ' -- drop table if exists contributions_individual';
drop table if exists contributions_individual;

select date_trunc('second', now()) || ' -- create table contributions_individual';
create table contributions_individual as
    select *
    from contributions_even_cycles c
    where
        (c.contributor_type is null or c.contributor_type in ('', 'I'))
        and c.recipient_type = 'P'
        and c.transaction_type in ('', '11', '15', '15e', '15j', '22y')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);

select date_trunc('second', now()) || ' -- create index contributions_individual_transaction_id on contributions_individual (transaction_id)';
create index contributions_individual_transaction_id on contributions_individual (transaction_id);


-- Only contributions from individuals to organizations

select date_trunc('second', now()) || ' -- drop table if exists contributions_individual_to_organization';
drop table if exists contributions_individual_to_organization;

select date_trunc('second', now()) || ' -- create table contributions_individual_to_organization';
create table contributions_individual_to_organization as
    select *
    from contributions_even_cycles c
    where
        (c.contributor_type is null or c.contributor_type in ('', 'I'))
        and c.recipient_type = 'C'
        and substring(c.recipient_category for 2) != 'Z4'
        and c.transaction_type in ('', '11', '15', '15e', '15j', '22y')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);

select date_trunc('second', now()) || ' -- create index contributions_individual_to_organization_transaction_id on contributions_individual_to_organization (transaction_id)';
create index contributions_individual_to_organization_transaction_id on contributions_individual_to_organization (transaction_id);


-- Only contributions that should be included in totals from organizations


select date_trunc('second', now()) || ' -- drop table if exists contributions_organization';
drop table if exists contributions_organization;

select date_trunc('second', now()) || ' -- create table contributions_organization';
create table contributions_organization as
    select *
    from contributions_even_cycles c
    where
        contributor_type = 'C'
        and recipient_type = 'P'
        and transaction_type in ('', '24k', '24r', '24z')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);

select date_trunc('second', now()) || ' -- create index contributions_organization_transaction_id on contributions_organization (transaction_id)';
create index contributions_organization_transaction_id on contributions_organization (transaction_id);


-- All contributions that we can aggregate


select date_trunc('second', now()) || ' -- drop table if exists contributions_all_relevant';
drop table if exists contributions_all_relevant;

select date_trunc('second', now()) || ' -- create table contributions_all_relevant';
create table contributions_all_relevant as
    select * from contributions_individual
    union all
    select * from contributions_individual_to_organization
    union all
    select * from contributions_organization;

select date_trunc('second', now()) || ' -- create index contributions_all_relevant__transaction_id__idx on contributions_all_relevant (transaction_id)';
create index contributions_all_relevant__transaction_id__idx on contributions_all_relevant (transaction_id);


-- Contributor Associations


select date_trunc('second', now()) || ' -- drop table if exists contributor_associations';
drop table if exists contributor_associations;

select date_trunc('second', now()) || ' -- create table contributor_associations';
create table contributor_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on lower(c.contributor_name) = lower(a.alias)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        a.verified = 't'
        -- use name matching for all organizations and state level individuals
        and (e.type = 'organization'
            or (e.type = 'individual' and c.transaction_namespace = 'urn:nimsp:transaction')) 
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.contributor_ext_id = a.value and a.value != ''
    where
        a.verified = 't'
        and (
            (a.namespace = 'urn:crp:individual' and c.transaction_namespace = 'urn:fec:transaction' and c.contributor_type = 'I')
            or (a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction' and c.contributor_type = 'C')
            or (a.namespace = 'urn:nimsp:individual' and c.transaction_namespace = 'urn:nimsp:transaction' and (c.contributor_type is null or c.contributor_type != 'C'))
            or (a.namespace = 'urn:nismp:organization' and c.transaction_namespace = 'urn:nimsp:transaction' and c.contributor_type = 'C')
        );

select date_trunc('second', now()) || ' -- create index contributor_associations_entity_id on contributor_associations (entity_id)';
create index contributor_associations_entity_id on contributor_associations (entity_id);
select date_trunc('second', now()) || ' -- create index contributor_associations_transaction_id on contributor_associations (transaction_id)';
create index contributor_associations_transaction_id on contributor_associations (transaction_id);


-- Organization Associations

select date_trunc('second', now()) || ' -- drop table if exists organization_associations';
drop table if exists organization_associations;

select date_trunc('second', now()) || ' -- create table organization_associations';
create table organization_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on lower(c.organization_name) = lower(a.alias)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        a.verified = 't'
        and e.type = 'organization'
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.organization_ext_id = a.value and a.value != ''
    where
        a.verified = 't'
        and ((a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'));

select date_trunc('second', now()) || ' -- create index organization_associations_entity_id on organization_associations (entity_id)';
create index organization_associations_entity_id on organization_associations (entity_id);
select date_trunc('second', now()) || ' -- create index organization_associations_transaction_id on organization_associations (transaction_id)';
create index organization_associations_transaction_id on organization_associations (transaction_id);

-- Parent Organization Associations

select date_trunc('second', now()) || ' -- drop table if exists parent_organization_associations';
drop table if exists parent_organization_associations;

select date_trunc('second', now()) || ' -- create table parent_organization_associations';
    create table parent_organization_associations as
        select a.entity_id, c.transaction_id
            from contribution_contribution c
            inner join matchbox_entityalias a
                on lower(c.parent_organization_name) = lower(a.alias)
            inner join matchbox_entity e
                on e.id = a.entity_id
            where
                a.verified = 't'
                and e.type = 'organization'
    union
        select a.entity_id, c.transaction_id
        from contribution_contribution c
        inner join matchbox_entityattribute a
            on c.parent_organization_ext_id = a.value and a.value != ''
        where
            a.verified = 't'
            and ((a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
                or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'));

select date_trunc('second', now()) || ' -- create index parent_organization_associations_entity_id on parent_organization_associations (entity_id)';
create index parent_organization_associations_entity_id on parent_organization_associations (entity_id);
select date_trunc('second', now()) || ' -- create index parent_organization_associations_transaction_id on parent_organization_associations (transaction_id)';
create index parent_organization_associations_transaction_id on parent_organization_associations (transaction_id);


-- Recipient Associations

select date_trunc('second', now()) || ' -- drop table if exists recipient_associations';
drop table if exists recipient_associations;

select date_trunc('second', now()) || ' -- create table recipient_associations';
create table recipient_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on lower(c.recipient_name) = lower(a.alias)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        a.verified = 't'
        and e.type = 'organization' -- name matching only for organizations; politicians should all have IDs
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.recipient_ext_id = a.value and a.value != ''
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        a.verified = 't'
        and ((a.namespace = 'urn:crp:recipient' and c.transaction_namespace = 'urn:fec:transaction' and c.recipient_type = 'P')
            or (a.namespace = 'urn:nimsp:recipient' and c.transaction_namespace = 'urn:nimsp:transaction' and c.recipient_type = 'P'));


select date_trunc('second', now()) || ' -- create index recipient_associations_entity_id on recipient_associations (entity_id)';
create index recipient_associations_entity_id on recipient_associations (entity_id);
select date_trunc('second', now()) || ' -- create index recipient_associations_transaction_id on recipient_associations (transaction_id)';
create index recipient_associations_transaction_id on recipient_associations (transaction_id);


-- Sparklines

select date_trunc('second', now()) || ' -- drop table if exists agg_contribution_sparklines';
drop table if exists agg_contribution_sparklines;

select date_trunc('second', now()) || ' -- create table agg_contribution_sparklines';
create table agg_contribution_sparklines as
    select
        entity_id,
        cycle,
        rank() over (partition by entity_id, cycle order by date_trunc('month', c.date)) as step,
        sum(amount) as amount
        from (
                select * from contributor_associations
                union
                select * from recipient_associations
                union
                select * from organization_associations
                union
                select * from parent_organization_associations
            ) a
            inner join contributions_all_relevant c using (transaction_id)
        where c.date between date(cycle-1 || '-01-01') and date(cycle || '-12-31')
        group by entity_id, cycle, date_trunc('month', c.date)

    union all

    select
        entity_id,
        -1 as cycle,
        rank() over (partition by entity_id order by date_trunc('quarter', c.date)) as step,
        sum(amount) as amount
        from (
                select * from contributor_associations
                union
                select * from recipient_associations
                union
                select * from organization_associations
                union
                select * from parent_organization_associations
            ) a
            inner join contributions_all_relevant c using (transaction_id)
        group by entity_id, date_trunc('quarter', c.date);
;

select date_trunc('second', now()) || ' -- create index agg_contribution_sparklines_idx on agg_contribution_sparklines (entity_id, cycle)';
create index agg_contribution_sparklines_idx on agg_contribution_sparklines (entity_id, cycle);



-- Sparklines by Party

select date_trunc('second', now()) || ' -- drop table if exists agg_contribution_sparklines_by_party';
drop table if exists agg_contribution_sparklines_by_party;

select date_trunc('second', now()) || ' -- create table agg_contribution_sparklines_by_party';
create table agg_contribution_sparklines_by_party as
    select
        entity_id,
        cycle,
        recipient_party,
        rank() over (partition by entity_id, cycle, recipient_party order by date_trunc('month', c.date)) as step,
        sum(amount) as amount
        from (
                select * from contributor_associations
                union
                select * from organization_associations
                union
                select * from parent_organization_associations
            ) a
            inner join contributions_all_relevant c using (transaction_id)
        where c.date between date(cycle-1 || '-01-01') and date(cycle || '-12-31')
        group by entity_id, cycle, recipient_party, date_trunc('month', c.date)

    union all

    select
        entity_id,
        -1 as cycle,
        recipient_party,
        rank() over (partition by entity_id, recipient_party order by date_trunc('quarter', c.date)) as step,
        sum(amount) as amount
        from (
                select * from contributor_associations
                union
                select * from organization_associations
                union
                select * from parent_organization_associations
            ) a
            inner join contributions_all_relevant c using (transaction_id)
        group by entity_id, recipient_party, date_trunc('quarter', c.date);

select date_trunc('second', now()) || ' -- create index agg_contribution_sparklines_by_party_idx on agg_contribution_sparklines_by_party (entity_id, cycle, recipient_party)';
create index agg_contribution_sparklines_by_party_idx on agg_contribution_sparklines_by_party (entity_id, cycle, recipient_party);



-- Entity Aggregates (Contribution Totals)


select date_trunc('second', now()) || ' -- drop table if exists agg_entities';
drop table if exists agg_entities;

select date_trunc('second', now()) || ' -- create table agg_entities';
create table agg_entities as
    select entity_id, coalesce(contrib_aggs.cycle, recip_aggs.cycle) as cycle, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count,
        coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
    from
        (select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
        from (select * from contributor_associations
            union select * from organization_associations
            union select * from parent_organization_associations) a
        inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id, transaction.cycle) as contrib_aggs
    full outer join
        (select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
        from recipient_associations a
            inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id, transaction.cycle) as recip_aggs
    using (entity_id, cycle)
union all
    select entity_id, -1 as cycle, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count,
        coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
    from
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from (select * from contributor_associations
            union select * from organization_associations
            union select * from parent_organization_associations) a
        inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id) as contrib_aggs
    full outer join
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from recipient_associations a
            inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id) as recip_aggs
    using (entity_id);

select date_trunc('second', now()) || ' -- create index agg_entities_idx on agg_entities (entity_id)';
create index agg_entities_idx on agg_entities (entity_id);



-- Industry Sector to Candidate


select date_trunc('second', now()) || ' -- drop table if exists agg_sectors_to_cand';
drop table if exists agg_sectors_to_cand;

select date_trunc('second', now()) || ' -- create table agg_sectors_to_cand';
create table agg_sectors_to_cand as
    select top.recipient_entity, top.sector, top.cycle, top.count, top.amount
    from
        (select ra.entity_id as recipient_entity, coalesce(substring(codes.catorder for 1), 'Y') as sector, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        left join agg_cat_map codes on c.contributor_category = codes.catcode
        group by ra.entity_id, coalesce(substring(codes.catorder for 1), 'Y'), c.cycle) top
    where
        rank <= :agg_top_n

    union all

    select top.recipient_entity, top.sector, -1, top.count, top.amount
    from
        (select ra.entity_id as recipient_entity, coalesce(substring(codes.catorder for 1), 'Y') as sector, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        left join agg_cat_map codes on c.contributor_category = codes.catcode
        group by ra.entity_id, coalesce(substring(codes.catorder for 1), 'Y')) top
    where
        rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_sectors_to_cand_idx on agg_sectors_to_cand (recipient_entity, cycle)';
create index agg_sectors_to_cand_idx on agg_sectors_to_cand (recipient_entity, cycle);


-- Candidates from Individual


select date_trunc('second', now()) || ' -- drop table if exists agg_cands_from_indiv';
drop table if exists agg_cands_from_indiv;

select date_trunc('second', now()) || ' -- create table agg_cands_from_indiv';
create table agg_cands_from_indiv as
    with individual_contributions_by_cycle as (
        select ca.entity_id as contributor_entity, coalesce(re.name, c.recipient_name) as recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        left join matchbox_entity re on re.id = ra.entity_id
        group by ca.entity_id, coalesce(re.name, c.recipient_name), coalesce(ra.entity_id, ''), cycle
    )

    select contributor_entity, recipient_name, recipient_entity, cycle, count, amount
    from individual_contributions_by_cycle
    where rank <= :agg_top_n

    union all

    select contributor_entity, recipient_name, recipient_entity, -1, count, amount
    from (
        select contributor_entity, recipient_name, recipient_entity, sum(count) as count, sum(amount) as amount,
            rank() over (partition by contributor_entity order by sum(amount) desc) as rank
        from individual_contributions_by_cycle
        group by contributor_entity, recipient_name, recipient_entity
    ) x
    where rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_cands_from_indiv_idx on agg_cands_from_indiv (contributor_entity, cycle)';
create index agg_cands_from_indiv_idx on agg_cands_from_indiv (contributor_entity, cycle);



-- Organizations from Individual


select date_trunc('second', now()) || ' -- drop table if exists agg_orgs_from_indiv';
drop table if exists agg_orgs_from_indiv;

select date_trunc('second', now()) || ' -- create table agg_orgs_from_indiv';
create table agg_orgs_from_indiv as
    with individual_to_org_contributions_by_cycle as (
    select ca.entity_id as contributor_entity, coalesce(re.name, c.recipient_name) as recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual_to_organization c
        inner join contributor_associations ca using(transaction_id)
        left join recipient_associations ra using (transaction_id)
        left join matchbox_entity re on re.id = ra.entity_id
        group by ca.entity_id, coalesce(re.name, c.recipient_name), coalesce(ra.entity_id, ''), cycle
    )
    select contributor_entity, recipient_name, recipient_entity, cycle, count, amount
    from individual_to_org_contributions_by_cycle
    where rank <= :agg_top_n

    union all

    select contributor_entity, recipient_name, recipient_entity, -1, count, amount
    from (
        select
            contributor_entity, recipient_name, recipient_entity, sum(count) as count, sum(amount) as amount,
            rank() over (partition by contributor_entity order by sum(amount) desc) as rank
        from individual_to_org_contributions_by_cycle
        group by contributor_entity, recipient_name, recipient_entity) x
    where rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_orgs_from_indiv_idx on agg_orgs_from_indiv (contributor_entity, cycle)';
create index agg_orgs_from_indiv_idx on agg_orgs_from_indiv (contributor_entity, cycle);



-- Organizations to Candidate


select date_trunc('second', now()) || ' -- drop table if exists agg_orgs_to_cand';
drop table if exists agg_orgs_to_cand;

select date_trunc('second', now()) || ' -- create table agg_orgs_to_cand';
create table agg_orgs_to_cand as
    with org_contributions_by_cycle as (
        select
            recipient_entity, organization_name, organization_entity, cycle,
            coalesce(top_pacs.count, 0) + coalesce(top_indivs.count, 0) as total_count,
            coalesce(top_pacs.count, 0) as pacs_count,
            coalesce(top_indivs.count, 0) as indivs_count,
            coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0) as total_amount,
            coalesce(top_pacs.amount, 0) as pacs_amount,
            coalesce(top_indivs.amount, 0) as indivs_amount,
            rank() over (partition by recipient_entity, cycle order by (coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0)) desc) as rank
        from (
            select ra.entity_id as recipient_entity, coalesce(oe.name, c.contributor_name) as organization_name,
                    coalesce(ca.entity_id, '') as organization_entity, cycle, count(*), sum(c.amount) as amount
                from contributions_organization c
                inner join recipient_associations ra using (transaction_id)
                left join contributor_associations ca using (transaction_id)
                left join matchbox_entity oe on oe.id = ca.entity_id
                group by ra.entity_id, coalesce(oe.name, c.contributor_name), coalesce(ca.entity_id, ''), cycle
            ) top_pacs
            full outer join (
                select ra.entity_id as recipient_entity, coalesce(oe.name, c.organization_name) as organization_name,
                    coalesce(oa.entity_id, '') as organization_entity, cycle, count(*) as count, sum(amount) as amount
                from contributions_individual c
                inner join recipient_associations ra using (transaction_id)
                left join organization_associations oa using (transaction_id)
                left join matchbox_entity oe on oe.id = oa.entity_id
                where organization_name != ''
                group by ra.entity_id, coalesce(oe.name, c.organization_name), coalesce(oa.entity_id, ''), cycle
            ) top_indivs
            using (recipient_entity, organization_name, organization_entity, cycle)
    )
    select
        recipient_entity, organization_name, organization_entity, cycle, total_count,
        pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from org_contributions_by_cycle
    where rank <= :agg_top_n

    union all

    select
        recipient_entity, organization_name, organization_entity, -1, total_count,
        pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from (
            select
                recipient_entity, organization_name, organization_entity, -1,
                sum(total_count) as total_count,
                sum(pacs_count) as pacs_count,
                sum(indivs_count) as indivs_count,
                sum(total_amount) as total_amount,
                sum(pacs_amount) as pacs_amount,
                sum(indivs_amount) as indivs_amount,
                rank() over (partition by recipient_entity order by sum(total_amount) desc) as rank
            from org_contributions_by_cycle
            group by recipient_entity, organization_name, organization_entity
    ) x
    where rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_orgs_to_cand_idx on agg_orgs_to_cand (recipient_entity, cycle)';
create index agg_orgs_to_cand_idx on agg_orgs_to_cand (recipient_entity, cycle);



-- Candidates from Organization


select date_trunc('second', now()) || ' -- drop table if exists agg_cands_from_org';
drop table if exists agg_cands_from_org;

select date_trunc('second', now()) || ' -- create table agg_cands_from_org';
create table agg_cands_from_org as
    with top_direct_and_indiv_contributions_by_cycle as (
        select organization_entity, recipient_name, recipient_entity, cycle,
            coalesce(top_direct.count, 0) + coalesce(top_indivs.count, 0) as total_count,
            coalesce(top_direct.count, 0) as pacs_count,
            coalesce(top_indivs.count, 0) as indivs_count,
            coalesce(top_direct.amount, 0) + coalesce(top_indivs.amount, 0) as total_amount,
            coalesce(top_direct.amount, 0) as pacs_amount,
            coalesce(top_indivs.amount, 0) as indivs_amount,
            rank() over (partition by organization_entity, cycle order by (coalesce(top_direct.amount, 0) + coalesce(top_indivs.amount, 0)) desc) as rank
        from (
            select ca.entity_id as organization_entity, coalesce(re.name, c.recipient_name) as recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
                cycle, count(*), sum(c.amount) as amount
            from contributions_organization c
            inner join (select * from organization_associations union select * from parent_organization_associations) ca using (transaction_id)
            left join recipient_associations ra using (transaction_id)
            left join matchbox_entity re on re.id = ra.entity_id
            group by ca.entity_id, coalesce(re.name, c.recipient_name), coalesce(ra.entity_id, ''), cycle
        ) top_direct
        full outer join (
            select oa.entity_id as organization_entity, coalesce(re.name, c.recipient_name) as recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
                cycle, count(*), sum(amount) as amount
            from contributions_individual c
            inner join (select * from organization_associations union select * from parent_organization_associations) oa using (transaction_id)
            left join recipient_associations ra using (transaction_id)
            left join matchbox_entity re on re.id = ra.entity_id
            group by oa.entity_id, coalesce(re.name, c.recipient_name), coalesce(ra.entity_id, ''), cycle
        ) top_indivs using (organization_entity, recipient_name, recipient_entity, cycle)
    )
    select organization_entity, recipient_name, recipient_entity, cycle,
        total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from top_direct_and_indiv_contributions_by_cycle
    where rank <= :agg_top_n

    union all

    select organization_entity, recipient_name, recipient_entity, -1,
        total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from (
        select organization_entity, recipient_name, recipient_entity,
            sum(total_count) as total_count, sum(pacs_count) as pacs_count, sum(indivs_count) as indivs_count,
            sum(total_amount) as total_amount, sum(pacs_amount) as pacs_amount, sum(indivs_amount) as indivs_amount,
            rank() over (partition by organization_entity order by sum(total_amount) desc) as rank
        from top_direct_and_indiv_contributions_by_cycle
        group by organization_entity, recipient_name, recipient_entity
    ) x
    where rank <= :agg_top_n
    ;

select date_trunc('second', now()) || ' -- create index agg_cands_from_org_idx on agg_cands_from_org (organization_entity, cycle)';
create index agg_cands_from_org_idx on agg_cands_from_org (organization_entity, cycle);



-- Party from Individual


select date_trunc('second', now()) || ' -- drop table if exists agg_party_from_indiv';
drop table if exists agg_party_from_indiv;

select date_trunc('second', now()) || ' -- create table agg_party_from_indiv';
create table agg_party_from_indiv as
    select ca.entity_id as contributor_entity, c.cycle, c.recipient_party, count(*), sum(c.amount) as amount
    from (select * from contributions_individual union all select * from contributions_individual_to_organization) c
    inner join contributor_associations ca using (transaction_id)
    group by ca.entity_id, c.cycle, c.recipient_party
union all
    select ca.entity_id as contributor_entity, -1, c.recipient_party, count(*), sum(c.amount) as amount
    from (select * from contributions_individual union all select * from contributions_individual_to_organization) c
    inner join contributor_associations ca using (transaction_id)
    group by ca.entity_id, c.recipient_party;

select date_trunc('second', now()) || ' -- create index agg_party_from_indiv_idx on agg_party_from_indiv (contributor_entity, cycle)';
create index agg_party_from_indiv_idx on agg_party_from_indiv (contributor_entity, cycle);



-- Party from Organization


select date_trunc('second', now()) || ' -- drop table if exists agg_party_from_org';
drop table if exists agg_party_from_org;

select date_trunc('second', now()) || ' -- create table agg_party_from_org';
create table agg_party_from_org as
    select oa.entity_id as organization_entity, c.cycle, c.recipient_party, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join (select * from organization_associations union select * from parent_organization_associations) oa using (transaction_id)
    group by oa.entity_id, c.cycle, c.recipient_party
union all
    select oa.entity_id as organization_entity, -1, c.recipient_party, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join (select * from organization_associations union select * from parent_organization_associations) oa using (transaction_id)
    group by oa.entity_id, c.recipient_party;

select date_trunc('second', now()) || ' -- create index agg_party_from_org_idx on agg_party_from_org (organization_entity, cycle)';
create index agg_party_from_org_idx on agg_party_from_org (organization_entity, cycle);



-- State/Fed from Organization


select date_trunc('second', now()) || ' -- drop table if exists agg_namespace_from_org';
drop table if exists agg_namespace_from_org;

select date_trunc('second', now()) || ' -- create table agg_namespace_from_org';
create table agg_namespace_from_org as
    select oa.entity_id as organization_entity, c.cycle, c.transaction_namespace, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join (select * from organization_associations union select * from parent_organization_associations) oa using (transaction_id)
    group by oa.entity_id, c.cycle, c.transaction_namespace
union all
    select oa.entity_id as organization_entity, -1, c.transaction_namespace, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join (select * from organization_associations union select * from parent_organization_associations) oa using (transaction_id)
    group by oa.entity_id, c.transaction_namespace;

select date_trunc('second', now()) || ' -- create index agg_namespace_from_org_idx on agg_namespace_from_org (organization_entity, cycle)';
create index agg_namespace_from_org_idx on agg_namespace_from_org (organization_entity, cycle);



-- In-state/Out-of-state to Politician


select date_trunc('second', now()) || ' -- drop table if exists agg_local_to_politician';
drop table if exists agg_local_to_politician;

select date_trunc('second', now()) || ' -- create table agg_local_to_politician';
create table agg_local_to_politician as
    select ra.entity_id as recipient_entity, c.cycle,
        case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end as local,
        count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, c.cycle, case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end
union all
    select ra.entity_id as recipient_entity, -1,
        case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end as local,
        count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end;

select date_trunc('second', now()) || ' -- create index agg_local_to_politician_idx on agg_local_to_politician (recipient_entity, cycle)';
create index agg_local_to_politician_idx on agg_local_to_politician (recipient_entity, cycle);



-- Indiv/PAC to Politician


select date_trunc('second', now()) || ' -- drop table if exists agg_contributor_type_to_politician';
drop table if exists agg_contributor_type_to_politician;

select date_trunc('second', now()) || ' -- create table agg_contributor_type_to_politician';
create table agg_contributor_type_to_politician as
    select ra.entity_id as recipient_entity, c.cycle, coalesce(c.contributor_type, '') as contributor_type, count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, c.cycle, coalesce(c.contributor_type, '')
union all
    select ra.entity_id as recipient_entity, -1, coalesce(c.contributor_type, '') as contributor_type, count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, coalesce(c.contributor_type, '');

select date_trunc('second', now()) || ' -- create index agg_contributor_type_to_politician_idx on agg_contributor_type_to_politician (recipient_entity, cycle)';
create index agg_contributor_type_to_politician_idx on agg_contributor_type_to_politician (recipient_entity, cycle);


select date_trunc('second', now()) || ' -- Finished computing contribution aggregates.';


