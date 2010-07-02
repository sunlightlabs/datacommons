-- Cycles: controls the cycles for which aggregates are computed
-- Mainly of using during development, when it helps to be able to regenerate the aggregates quickly.

begin;
drop table if exists agg_cycles cascade;

create table agg_cycles as
--    values (2005), (2006), (2007), (2008), (2009), (2010);
    select distinct cycle from contribution_contribution;

commit;
-- Top N: the number of rows to generate for each aggregate

\set agg_top_n 10
--\set agg_top_n 100


-- CatCodes that should not be included in totals.
-- Taken from the NIMSP column CatCodes.TopSuppress.

begin;
drop table if exists agg_suppressed_catcodes;

create table agg_suppressed_catcodes as
    values ('Z2100'), ('Z2200'), ('Z2300'), ('Z2400'), ('Z7777'), ('Z8888'),
        ('Z9010'), ('Z9020'), ('Z9030'), ('Z9040'),
        ('Z9100'), ('Z9500'), ('Z9600'), ('Z9700'), ('Z9999');
commit;


-- Adjust the odd-year cycles upward

begin;
drop view if exists contributions_even_cycles cascade;

create view contributions_even_cycles as
    select transaction_id, transaction_namespace, transaction_type, amount,
        case when cycle % 2 = 0 then cycle else cycle + 1 end as cycle, date,
        contributor_name, contributor_type, contributor_category, contributor_category_order, contributor_state,
        organization_name, parent_organization_name,
        recipient_name, recipient_type, recipient_party, recipient_state
    from contribution_contribution;
commit;


-- Only contributions that should be included in totals from individuals to politicians

begin;
drop view if exists contributions_individual; -- TODO: remove after the next time aggregates are generated
drop table if exists contributions_individual;

create table contributions_individual as
    select *
    from contributions_even_cycles c
    where
        (c.contributor_type is null or c.contributor_type in ('', 'I'))
        and c.recipient_type = 'P'
        and c.transaction_type in ('', '11', '15', '15e', '15j', '22y')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);

create index contributions_individual_transaction_id on contributions_individual (transaction_id);
commit;

-- Only contributions from individuals to organizations
begin;
drop view if exists contributions_individual_to_organization; -- TODO: remove after the next time aggregates are generated
drop table if exists contributions_individual_to_organization;

create table contributions_individual_to_organization as
    select *
    from contributions_even_cycles c
    where
        (c.contributor_type is null or c.contributor_type in ('', 'I'))
        and c.recipient_type = 'C'
        and c.transaction_type in ('', '11', '15', '15e', '15j', '22y')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);

create index contributions_individual_to_organization_transaction_id on contributions_individual_to_organization (transaction_id);
commit;

-- Only contributions that should be included in totals from organizations

begin;
drop view if exists contributions_organization; -- TODO: remove after the next time aggregates are generated
drop table if exists contributions_organization;

create table contributions_organization as
    select *
    from contributions_even_cycles c
    where
        contributor_type = 'C'
        and recipient_type = 'P'
        and transaction_type in ('', '24k', '24r', '24z')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and cycle in (select * from agg_cycles);

create index contributions_organization_transaction_id on contributions_organization (transaction_id);
commit;

-- All contributions that we can aggregate

begin;
drop table if exists contributions_all_relevant;

create table contributions_all_relevant as
    select * from contributions_individual
    union all
    select * from contributions_individual_to_organization
    union all
    select * from contributions_organization;

create index contributions_all_relevant__transaction_id__idx on contributions_all_relevant (transaction_id);
commit;

-- Contributor Associations

begin;
drop table if exists contributor_associations;

create table contributor_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on c.contributor_name = a.alias
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        a.verified = 't'
        and e.type in ('individual', 'organization')
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.contributor_ext_id = a.value and a.value != ''
    where
        a.verified = 't'
        and ((a.namespace in ('urn:crp:individual', 'urn:crp:organization') and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace in ('urn:nimsp:individual', 'urn:nimsp:organization') and c.transaction_namespace = 'urn:nimsp:transaction'));

create index contributor_associations_entity_id on contributor_associations (entity_id);
create index contributor_associations_transaction_id on contributor_associations (transaction_id);

commit;

-- Organization Associations

begin;
drop table if exists organization_associations;

create table organization_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on c.organization_name = a.alias
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        a.verified = 't'
        and e.type = 'organization'
union
    select a.entity_id, c.transaction_id
        from contribution_contribution c
        inner join matchbox_entityalias a
            on c.parent_organization_name = a.alias
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
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'))
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.parent_organization_ext_id = a.value and a.value != ''
    where
        a.verified = 't'
        and ((a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction'));

create index organization_associations_entity_id on organization_associations (entity_id);
create index organization_associations_transaction_id on organization_associations (transaction_id);

commit;

-- Recipient Associations

begin;
drop table if exists recipient_associations;

create table recipient_associations as
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityalias a
        on c.recipient_name = a.alias
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        a.verified = 't'
        and e.type in ('organization')
union
    select a.entity_id, c.transaction_id
    from contribution_contribution c
    inner join matchbox_entityattribute a
        on c.recipient_ext_id = a.value and a.value != ''
    where
        a.verified = 't'
        and ((a.namespace = 'urn:crp:recipient' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:recipient' and c.transaction_namespace = 'urn:nimsp:transaction'));


create index recipient_associations_entity_id on recipient_associations (entity_id);
create index recipient_associations_transaction_id on recipient_associations (transaction_id);
commit;


-- Sparklines

\set sparkline_resolution 24

begin;
drop table if exists agg_contribution_sparklines;

create table agg_contribution_sparklines as
    select entity_id, cycle,
        ((c.date - date(cycle-1 || '-01-01')) * :sparkline_resolution) / (date(cycle || '-12-31') - date(cycle-1 || '-01-01')) as step,
        sum(amount) as amount
        from (
                select * from contributor_associations
                union
                select * from recipient_associations
                union
                select * from organization_associations
            ) a
            inner join contributions_all_relevant c using (transaction_id)
        where c.date between date(cycle-1 || '-01-01') and date(cycle || '-12-31')
        group by entity_id, cycle, ((c.date - date(cycle-1 || '-01-01')) * :sparkline_resolution) / (date(cycle || '-12-31') - date(cycle-1 || '-01-01'));

create index agg_contribution_sparklines_idx on agg_contribution_sparklines (entity_id, cycle);
commit;


-- Sparklines by Party

\set sparkline_resolution 24

begin;
drop table if exists agg_contribution_sparklines_by_party;

create table agg_contribution_sparklines_by_party as
    select
        entity_id,
        cycle,
        recipient_party,
        ((c.date - date(cycle-1 || '-01-01')) * :sparkline_resolution) / (date(cycle || '-12-31') - date(cycle-1 || '-01-01')) as step,
        sum(amount) as amount
        from (
                select * from contributor_associations
                union
                select * from organization_associations
            ) a
            inner join contributions_all_relevant c using (transaction_id)
        where c.date between date(cycle-1 || '-01-01') and date(cycle || '-12-31')
        group by entity_id, cycle, recipient_party, ((c.date - date(cycle-1 || '-01-01')) * :sparkline_resolution) / (date(cycle || '-12-31') - date(cycle-1 || '-01-01'));

create index agg_contribution_sparklines_by_party_idx on agg_contribution_sparklines_by_party (entity_id, cycle, recipient_party);
commit;


-- Entity Aggregates (Contribution Totals)

begin;
drop table if exists agg_entities;

create table agg_entities as
    select entity_id, coalesce(contrib_aggs.cycle, recip_aggs.cycle) as cycle, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count,
        coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
    from
        (select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
        from (select * from contributor_associations union select * from organization_associations) a
            inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id, transaction.cycle) as contrib_aggs
    full outer join
        (select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
        from recipient_associations a
            inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id, transaction.cycle) as recip_aggs
    using (entity_id, cycle)
union
    select entity_id, -1 as cycle, coalesce(contrib_aggs.count, 0) as contributor_count, coalesce(recip_aggs.count, 0) as recipient_count,
        coalesce(contrib_aggs.sum, 0) as contributor_amount, coalesce(recip_aggs.sum, 0) as recipient_amount
    from
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from (select * from contributor_associations union select * from organization_associations) a
            inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id) as contrib_aggs
    full outer join
        (select a.entity_id, count(transaction), sum(transaction.amount)
        from recipient_associations a
            inner join contributions_all_relevant transaction using (transaction_id)
        group by a.entity_id) as recip_aggs
    using (entity_id);

create index agg_entities_idx on agg_entities (entity_id);
commit;


-- Industry Sector to Candidate

begin;
drop table if exists agg_sectors_to_cand;

create table agg_sectors_to_cand as
    select top.recipient_entity, top.sector, top.cycle, top.count, top.amount
    from
        (select ra.entity_id as recipient_entity, substring(c.contributor_category_order for 1) as sector, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, substring(c.contributor_category_order for 1), c.cycle) top
    where
        rank <= :agg_top_n
union
    select top.recipient_entity, top.sector, -1, top.count, top.amount
    from
        (select ra.entity_id as recipient_entity, substring(c.contributor_category_order for 1) as sector, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, substring(c.contributor_category_order for 1)) top
    where
        rank <= :agg_top_n;

create index agg_sectors_to_cand_idx on agg_sectors_to_cand (recipient_entity, cycle);
commit;


-- Industry Category Orders to Candidate

begin;
drop table if exists agg_cat_orders_to_cand;

create table agg_cat_orders_to_cand as
    select top.recipient_entity, top.sector, top.contributor_category_order, top.cycle, top.count, top.amount
    from
        (select ra.entity_id as recipient_entity, substring(c.contributor_category_order for 1) as sector, c.contributor_category_order, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, substring(c.contributor_category_order for 1), c.cycle order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, substring(c.contributor_category_order for 1), c.contributor_category_order, c.cycle) top
    where
        rank <= :agg_top_n
union
    select top.recipient_entity, top.sector, top.contributor_category_order, -1, top.count, top.amount
    from
        (select ra.entity_id as recipient_entity, substring(c.contributor_category_order for 1) as sector, c.contributor_category_order, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, substring(c.contributor_category_order for 1) order by sum(amount) desc) as rank
        from (select * from contributions_individual union select * from contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, substring(c.contributor_category_order for 1), c.contributor_category_order) top
    where
        rank <= :agg_top_n;

create index agg_cat_orders_to_cand_idx on agg_cat_orders_to_cand (recipient_entity, sector, cycle);
commit;


-- Candidates from Individual

begin;
drop table if exists agg_cands_from_indiv;

create table agg_cands_from_indiv as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= :agg_top_n
union
    select top.contributor_entity, top.recipient_name, top.recipient_entity, -1, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
            count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id order by sum(amount) desc) as rank
        from contributions_individual c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, '')) top
    where
        rank <= :agg_top_n;

create index agg_cands_from_indiv_idx on agg_cands_from_indiv (contributor_entity, cycle);
commit;


-- Committees from Individual

begin;
drop table if exists agg_orgs_from_indiv;

create table agg_orgs_from_indiv as
    select top.contributor_entity, top.recipient_name, top.recipient_entity, top.cycle, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual_to_organization c
        inner join contributor_associations ca using(transaction_id)
        left join recipient_associations ra using (transaction_id)
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, ''), cycle) top
    where
        rank <= :agg_top_n
union
    select top.contributor_entity, top.recipient_name, top.recipient_entity, -1, top.count, top.amount
    from (select ca.entity_id as contributor_entity, c.recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
            count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id order by sum(amount) desc) as rank
        from contributions_individual_to_organization c
        inner join contributor_associations ca using(transaction_id)
        left join recipient_associations ra using (transaction_id)
        group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, '')) top
    where
        rank <= :agg_top_n;

create index agg_orgs_from_indiv_idx on agg_orgs_from_indiv (contributor_entity, cycle);
commit;


-- Organizations to Candidate

begin;
drop table if exists agg_orgs_to_cand;

create table agg_orgs_to_cand as
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
            using (recipient_entity, organization_name, organization_entity, cycle)
        ) top
    where
        rank <= :agg_top_n
union
    select  top.recipient_entity, top.organization_name, top.organization_entity, -1,
            top.total_count, top.pacs_count, top.indivs_count, top.total_amount, top.pacs_amount, top.indivs_amount
    from
        (select recipient_entity, organization_name, organization_entity,
            coalesce(top_pacs.count, 0) + coalesce(top_indivs.count, 0) as total_count, coalesce(top_pacs.count, 0) as pacs_count, coalesce(top_indivs.count, 0) as indivs_count,
            coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0) as total_amount, coalesce(top_pacs.amount, 0) as pacs_amount, coalesce(top_indivs.amount, 0) as indivs_amount,
            rank() over (partition by recipient_entity order by (coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0)) desc) as rank
        from
                (select ra.entity_id as recipient_entity, c.contributor_name as organization_name, coalesce(ca.entity_id, '') as organization_entity,
                    count(*), sum(c.amount) as amount
                from contributions_organization c
                inner join recipient_associations ra using (transaction_id)
                left join contributor_associations ca using (transaction_id)
                group by ra.entity_id, c.contributor_name, coalesce(ca.entity_id, '')) top_pacs
            full outer join
                (select ra.entity_id as recipient_entity,
                    case when parent_organization_name != '' then parent_organization_name
                        else organization_name end as organization_name,
                    coalesce(oa.entity_id, '') as organization_entity,
                    count(*) as count, sum(amount) as amount
                from contributions_individual c
                inner join recipient_associations ra using (transaction_id)
                left join organization_associations oa using (transaction_id)
                where
                    organization_name != '' or parent_organization_name != ''
                group by ra.entity_id,
                    case when parent_organization_name != '' then parent_organization_name
                        else organization_name end,
                    coalesce(oa.entity_id, '')) top_indivs
                using (recipient_entity, organization_name, organization_entity)) top
    where
        rank <= :agg_top_n;

create index agg_orgs_to_cand_idx on agg_orgs_to_cand (recipient_entity, cycle);
commit;


-- Candidates from Organization

begin;
drop table if exists agg_cands_from_org;

create table agg_cands_from_org as
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
                inner join organization_associations ca using (transaction_id)
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
        rank <= :agg_top_n
union
    select  top.organization_entity, top.recipient_name, top.recipient_entity, -1,
            top.total_count, top.pacs_count, top.indivs_count, top.total_amount, top.pacs_amount, top.indivs_amount
    from
        (select organization_entity, recipient_name, recipient_entity,
            coalesce(top_direct.count, 0) + coalesce(top_indivs.count, 0) as total_count, coalesce(top_direct.count, 0) as pacs_count, coalesce(top_indivs.count, 0) as indivs_count,
            coalesce(top_direct.amount, 0) + coalesce(top_indivs.amount, 0) as total_amount, coalesce(top_direct.amount, 0) as pacs_amount, coalesce(top_indivs.amount, 0) as indivs_amount,
            rank() over (partition by organization_entity order by (coalesce(top_direct.amount, 0) + coalesce(top_indivs.amount, 0)) desc) as rank
        from
                (select ca.entity_id as organization_entity, c.recipient_name as recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
                    count(*), sum(c.amount) as amount
                from contributions_organization c
                inner join contributor_associations ca using (transaction_id)
                left join recipient_associations ra using (transaction_id)
                group by ca.entity_id, c.recipient_name, coalesce(ra.entity_id, '')) top_direct
            full outer join
                (select oa.entity_id as organization_entity, c.recipient_name as recipient_name, coalesce(ra.entity_id, '') as recipient_entity,
                    count(*), sum(amount) as amount
                from contributions_individual c
                inner join organization_associations oa using (transaction_id)
                left join recipient_associations ra using (transaction_id)
                group by oa.entity_id, c.recipient_name, coalesce(ra.entity_id, '')) top_indivs
            using (organization_entity, recipient_name, recipient_entity)) top
    where
        rank <= :agg_top_n;

create index agg_cands_from_org_idx on agg_cands_from_org (organization_entity, cycle);
commit;


-- Party from Individual

begin;
drop table if exists agg_party_from_indiv;

create table agg_party_from_indiv as
    select ca.entity_id as contributor_entity, c.cycle, c.recipient_party, count(*), sum(c.amount) as amount
    from (select * from contributions_individual union all select * from contributions_individual_to_organization) c
    inner join contributor_associations ca using (transaction_id)
    group by ca.entity_id, c.cycle, c.recipient_party
union
    select ca.entity_id as contributor_entity, -1, c.recipient_party, count(*), sum(c.amount) as amount
    from (select * from contributions_individual union all select * from contributions_individual_to_organization) c
    inner join contributor_associations ca using (transaction_id)
    group by ca.entity_id, c.recipient_party;

create index agg_party_from_indiv_idx on agg_party_from_indiv (contributor_entity, cycle);
commit;


-- Party from Organization

begin;
drop table if exists agg_party_from_org;

create table agg_party_from_org as
    select oa.entity_id as organization_entity, c.cycle, c.recipient_party, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join organization_associations oa using (transaction_id)
    group by oa.entity_id, c.cycle, c.recipient_party
union
    select oa.entity_id as organization_entity, -1, c.recipient_party, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join organization_associations oa using (transaction_id)
    group by oa.entity_id, c.recipient_party;

create index agg_party_from_org_idx on agg_party_from_org (organization_entity, cycle);
commit;


-- State/Fed from Organization

begin;
drop table if exists agg_namespace_from_org;

create table agg_namespace_from_org as
    select oa.entity_id as organization_entity, c.cycle, c.transaction_namespace, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join organization_associations oa using (transaction_id)
    group by oa.entity_id, c.cycle, c.transaction_namespace
union
    select oa.entity_id as organization_entity, -1, c.transaction_namespace, count(*), sum(amount) as amount
    from contributions_all_relevant c
    inner join organization_associations oa using (transaction_id)
    group by oa.entity_id, c.transaction_namespace;

create index agg_namespace_from_org_idx on agg_namespace_from_org (organization_entity, cycle);
commit;


-- In-state/Out-of-state to Politician

begin;
drop table if exists agg_local_to_politician;

create table agg_local_to_politician as
    select ra.entity_id as recipient_entity, c.cycle,
        case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end as local,
        count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, c.cycle, case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end
union
    select ra.entity_id as recipient_entity, -1,
        case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end as local,
        count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, case when c.contributor_state = c.recipient_state then 'in-state' else 'out-of-state' end;

create index agg_local_to_politician_idx on agg_local_to_politician (recipient_entity, cycle);
commit;


-- Indiv/PAC to Politician

begin;
drop table if exists agg_contributor_type_to_politician;

create table agg_contributor_type_to_politician as
    select ra.entity_id as recipient_entity, c.cycle, coalesce(c.contributor_type, '') as contributor_type, count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, c.cycle, coalesce(c.contributor_type, '')
union
    select ra.entity_id as recipient_entity, -1, coalesce(c.contributor_type, '') as contributor_type, count(*), sum(amount) as amount
    from (select * from contributions_individual union select * from contributions_organization) c
    inner join recipient_associations ra using (transaction_id)
    group by ra.entity_id, coalesce(c.contributor_type, '');

create index agg_contributor_type_to_politician_idx on agg_contributor_type_to_politician (recipient_entity, cycle);
commit;



