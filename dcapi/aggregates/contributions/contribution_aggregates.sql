select date_trunc('second', now()) || ' -- Starting contribution aggregate computation...';

-- Top N: the number of rows to generate for each aggregate

\set agg_top_n 10


-- Entity Aggregates (Contribution Totals)


select date_trunc('second', now()) || ' -- drop table if exists agg_entities';
drop table if exists agg_entities cascade;

select date_trunc('second', now()) || ' -- create table agg_entities';
create table agg_entities as
    with contribs_by_cycle as (
        select
            entity_id,
            coalesce(contrib_aggs.cycle, recip_aggs.cycle) as cycle,
            coalesce(contrib_aggs.count, 0)                as contributor_count,
            coalesce(recip_aggs.count, 0)                  as recipient_count,
            coalesce(contrib_aggs.sum, 0)                  as contributor_amount,
            coalesce(recip_aggs.sum, 0)                    as recipient_amount
        from (
            select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
            from (
                table contributor_associations
                union table organization_associations
                union table parent_organization_associations
                union all table industry_associations
            ) a
            inner join contributions_all_relevant transaction using (transaction_id)
            group by a.entity_id, transaction.cycle
        ) as contrib_aggs
        full outer join (
            select a.entity_id, transaction.cycle, count(transaction), sum(transaction.amount)
            from recipient_associations a
            inner join contributions_all_relevant transaction using (transaction_id)
            group by a.entity_id, transaction.cycle
        ) as recip_aggs using (entity_id, cycle)
    )

    select
        entity_id,
        cycle,
        contributor_count,
        recipient_count,
        contributor_amount,
        recipient_amount
    from contribs_by_cycle

    union all

    select
        entity_id,
        -1                      as cycle,
        sum(contributor_count)  as contributor_count,
        sum(recipient_count)    as recipient_count,
        sum(contributor_amount) as contributor_amount,
        sum(recipient_amount)   as recipient_amount
    from contribs_by_cycle
    group by entity_id;

select date_trunc('second', now()) || ' -- create index agg_entities_idx on agg_entities (entity_id)';
create index agg_entities_idx on agg_entities (entity_id);


-- Industry Sector to Candidate

select date_trunc('second', now()) || ' -- drop table if exists agg_sectors_to_cand';
drop table if exists agg_sectors_to_cand cascade;

select date_trunc('second', now()) || ' -- create table agg_sectors_to_cand';
create table agg_sectors_to_cand as
    with contribs_by_cycle as (
        select ra.entity_id as recipient_entity, coalesce(substring(codes.catorder for 1), 'Y') as sector, c.cycle, count(*), sum(amount) as amount,
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from (table contributions_individual union table contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        left join agg_cat_map codes on c.contributor_category = codes.catcode
        group by ra.entity_id, coalesce(substring(codes.catorder for 1), 'Y'), c.cycle
    )

    select recipient_entity, sector, cycle, count, amount
    from contribs_by_cycle
    where rank <= :agg_top_n

    union all

    select recipient_entity, sector, -1, count, amount
    from (
        select recipient_entity, sector, sum(count) as count, sum(amount) as amount,
            rank() over (partition by recipient_entity order by sum(amount) desc) as rank
        from contribs_by_cycle
        group by recipient_entity, sector
    )x
    where rank <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index agg_sectors_to_cand_idx on agg_sectors_to_cand (recipient_entity, cycle)';
create index agg_sectors_to_cand_idx on agg_sectors_to_cand (recipient_entity, cycle);


-- Industry to Candidate

select date_trunc('second', now()) || ' -- drop table if exists agg_industries_to_cand';
drop table if exists agg_industries_to_cand cascade;

select date_trunc('second', now()) || ' -- create table agg_industries_to_cand';
create table agg_industries_to_cand as
    with contribs_by_cycle as (
        select
            ra.entity_id as recipient_entity,
            coalesce(ia.entity_id, (select entity_id from matchbox_entityattribute where value = 'Y00')) as industry_entity,
            coalesce(me.name, 'UNKNOWN') as industry,
            c.cycle,
            count(*),
            sum(amount) as amount,
            rank() over (partition by ra.entity_id, cycle order by sum(amount) desc) as rank
        from (table contributions_individual union table contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        left join industry_associations ia using (transaction_id)
        left join matchbox_entity me on me.id = ia.entity_id
        left join matchbox_entityattribute ma on ma.entity_id = ia.entity_id
        where
            -- exclude subindustries
            coalesce(ma.namespace, 'urn:crp:industry') = 'urn:crp:industry'
            and substring(c.contributor_category for 1) not in ('', 'Y', 'Z')
        group by ra.entity_id, ia.entity_id, coalesce(me.name, 'UNKNOWN'), c.cycle
    )

    select recipient_entity, industry_entity, industry, cycle, count, amount
    from contribs_by_cycle
    where rank <= :agg_top_n

    union all

    select recipient_entity, industry_entity, industry, -1, count, amount
    from (
        select recipient_entity, industry_entity, industry, sum(count) as count, sum(amount) as amount,
            rank() over (partition by recipient_entity order by sum(amount) desc) as rank
        from contribs_by_cycle
        group by recipient_entity, industry_entity, industry
    ) x
    where rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_industries_to_cand_idx on agg_industries_to_cand (recipient_entity, cycle)';
create index agg_industries_to_cand_idx on agg_industries_to_cand (recipient_entity, cycle);


-- Unknown Industry Portion

select date_trunc('second', now()) || ' -- drop table if exists agg_unknown_industries_to_cand';
drop table if exists agg_unknown_industries_to_cand cascade;

select date_trunc('second', now()) || ' -- create table agg_unknown_industries_to_cand';
create table agg_unknown_industries_to_cand as
    with unknown_by_cycle as (
        select
            ra.entity_id as recipient_entity,
            c.cycle,
            count(*),
            sum(amount) as amount
        from (table contributions_individual union table contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        where
            substring(c.contributor_category for 1) in ('', 'Y', 'Z')
        group by ra.entity_id, c.cycle
    )

    table unknown_by_cycle

    union all

    select recipient_entity, -1 as cycle, sum(count) as count, sum(amount) as amount
    from unknown_by_cycle
    group by recipient_entity;

select date_trunc('second', now()) || ' -- create index agg_unknown_industries_to_cand_idx on agg_unknown_industries_to_cand (recipient_entity, cycle);';
create index agg_unknown_industries_to_cand_idx on agg_unknown_industries_to_cand (recipient_entity, cycle);


-- Individuals: Top Politician Recipients

select date_trunc('second', now()) || ' -- drop table if exists agg_cands_from_indiv';
drop table if exists agg_cands_from_indiv cascade;

select date_trunc('second', now()) || ' -- create table agg_cands_from_indiv';
create table agg_cands_from_indiv as
    with individual_contributions_by_cycle as (
        select ca.entity_id as contributor_entity, coalesce(re.name, c.recipient_name) as recipient_name, ra.entity_id as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual c
        inner join contributor_associations ca using (transaction_id)
        left join recipient_associations ra using (transaction_id)
        left join matchbox_entity re on re.id = ra.entity_id
        group by ca.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
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


-- Individuals: Top Organization Recipients

select date_trunc('second', now()) || ' -- drop table if exists agg_orgs_from_indiv';
drop table if exists agg_orgs_from_indiv cascade;

select date_trunc('second', now()) || ' -- create table agg_orgs_from_indiv';
create table agg_orgs_from_indiv as
    with individual_to_org_contributions_by_cycle as (
    select ca.entity_id as contributor_entity, coalesce(re.name, c.recipient_name) as recipient_name, ra.entity_id as recipient_entity,
            cycle, count(*), sum(c.amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from contributions_individual_to_organization c
        inner join contributor_associations ca using(transaction_id)
        left join recipient_associations ra using (transaction_id)
        left join matchbox_entity re on re.id = ra.entity_id
        group by ca.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
    )

    select contributor_entity, recipient_name, recipient_entity, cycle, count, amount
    from individual_to_org_contributions_by_cycle
    where rank <= :agg_top_n

    union all

    select contributor_entity, recipient_name, recipient_entity, -1, count, amount
    from (
        select contributor_entity, recipient_name, recipient_entity, sum(count) as count, sum(amount) as amount,
            rank() over (partition by contributor_entity order by sum(amount) desc) as rank
        from individual_to_org_contributions_by_cycle
        group by contributor_entity, recipient_name, recipient_entity
    ) x
    where rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_orgs_from_indiv_idx on agg_orgs_from_indiv (contributor_entity, cycle)';
create index agg_orgs_from_indiv_idx on agg_orgs_from_indiv (contributor_entity, cycle);


-- Politicians: Top Donor Organizations

select date_trunc('second', now()) || ' -- drop table if exists agg_orgs_to_cand';
drop table if exists agg_orgs_to_cand cascade;

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
                    ca.entity_id as organization_entity, cycle, count(*), sum(c.amount) as amount
                from contributions_organization c
                inner join recipient_associations ra using (transaction_id)
                left join biggest_organization_associations ca using (transaction_id)
                left join matchbox_entity oe on oe.id = ca.entity_id
                where
                    lower(organization_name) not in (select * from agg_suppressed_orgnames)
                group by ra.entity_id, coalesce(oe.name, c.contributor_name), ca.entity_id, cycle
            ) top_pacs
            full outer join (
                select ra.entity_id as recipient_entity, coalesce(oe.name, case when organization_name != '' then c.organization_name else contributor_name end) as organization_name,
                    oa.entity_id as organization_entity, cycle, count(*) as count, sum(amount) as amount
                from contributions_individual c
                inner join recipient_associations ra using (transaction_id)
                left join biggest_organization_associations oa using (transaction_id)
                left join matchbox_entity oe on oe.id = oa.entity_id
                where
                    lower(case when organization_name != '' then c.organization_name else contributor_name end) not in (select * from agg_suppressed_orgnames)
                group by ra.entity_id, coalesce(oe.name, case when organization_name != '' then c.organization_name else contributor_name end), oa.entity_id, cycle
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
            recipient_entity, organization_name, organization_entity,
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


-- Organizations: Top Politician Recipients

select date_trunc('second', now()) || ' -- drop table if exists agg_cands_from_org';
drop table if exists agg_cands_from_org cascade;

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
            select ca.entity_id as organization_entity, coalesce(re.name, c.recipient_name) as recipient_name, ra.entity_id as recipient_entity,
                cycle, count(*), sum(c.amount) as amount
            from contributions_organization c
            inner join (table organization_associations union table parent_organization_associations union all table industry_associations) ca using (transaction_id)
            left join recipient_associations ra using (transaction_id)
            left join matchbox_entity re on re.id = ra.entity_id
            where coalesce(re.name, c.recipient_name) != ''
            group by ca.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
        ) top_direct
        full outer join (
            select oa.entity_id as organization_entity, coalesce(re.name, c.recipient_name) as recipient_name, ra.entity_id as recipient_entity,
                cycle, count(*), sum(amount) as amount
            from contributions_individual c
            inner join (table contributor_associations union table organization_associations union table parent_organization_associations union all table industry_associations) oa using (transaction_id)
            left join recipient_associations ra using (transaction_id)
            left join matchbox_entity re on re.id = ra.entity_id
            -- todo: this table is now redundant with the agg_cands_from_indiv. Should refactor handler to use this table.
            group by oa.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
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


-- Organizations: Top PAC Recipients

select date_trunc('second', now()) || ' -- drop table if exists agg_pacs_from_org';
drop table if exists agg_pacs_from_org cascade;

select date_trunc('second', now()) || ' -- create table agg_pacs_from_org';
create table agg_pacs_from_org as
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
            select ca.entity_id as organization_entity, coalesce(re.name, c.recipient_name) as recipient_name, ra.entity_id as recipient_entity,
                cycle, count(*), sum(c.amount) as amount
            from contributions_org_to_pac c
            inner join (table organization_associations union table parent_organization_associations union all table industry_associations) ca using (transaction_id)
            left join recipient_associations ra using (transaction_id)
            left join matchbox_entity re on re.id = ra.entity_id
            group by ca.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
        ) top_direct
        full outer join (
            select oa.entity_id as organization_entity, coalesce(re.name, c.recipient_name) as recipient_name, ra.entity_id as recipient_entity,
                cycle, count(*), sum(amount) as amount
            from contributions_individual_to_organization c
            inner join (table contributor_associations
                union table organization_associations
                union table parent_organization_associations
                union all table industry_associations
            ) oa using (transaction_id)
            left join recipient_associations ra using (transaction_id)
            left join matchbox_entity re on re.id = ra.entity_id
            group by oa.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
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

select date_trunc('second', now()) || ' -- create index agg_pacs_from_org_idx on agg_pacs_from_org (organization_entity, cycle)';
create index agg_pacs_from_org_idx on agg_pacs_from_org (organization_entity, cycle);




-- Party from Individual

select date_trunc('second', now()) || ' -- drop table if exists agg_party_from_indiv';
drop table if exists agg_party_from_indiv cascade;

select date_trunc('second', now()) || ' -- create table agg_party_from_indiv';
create table agg_party_from_indiv as
    with contribs_by_cycle as (
        select ca.entity_id as contributor_entity, c.cycle, c.recipient_party, count(*), sum(c.amount) as amount
        from (table contributions_individual union all table contributions_individual_to_organization) c
        inner join contributor_associations ca using (transaction_id)
        where recipient_party != '' and contributor_type = 'I' AND (transaction_namespace = 'urn:nimsp:transaction' or contributor_ext_id != '')
        group by ca.entity_id, c.cycle, c.recipient_party
    )

    select contributor_entity, cycle, recipient_party, count, amount
    from contribs_by_cycle

    union all

    select contributor_entity, -1, recipient_party, sum(count) as count, sum(amount) as amount
    from contribs_by_cycle
    group by contributor_entity, recipient_party;

select date_trunc('second', now()) || ' -- create index agg_party_from_indiv_idx on agg_party_from_indiv (contributor_entity, cycle)';
create index agg_party_from_indiv_idx on agg_party_from_indiv (contributor_entity, cycle);


-- Party from Organization

select date_trunc('second', now()) || ' -- drop table if exists agg_party_from_org';
drop table if exists agg_party_from_org cascade;

select date_trunc('second', now()) || ' -- create table agg_party_from_org';
create table agg_party_from_org as
   with contribs_by_cycle as (
    select oa.entity_id as organization_entity, c.cycle, case when c.recipient_party != '' then c.recipient_party else 'None' end as recipient_party, count(*), sum(amount) as amount
        from contributions_all_relevant c
        inner join (table contributor_associations union table organization_associations union table parent_organization_associations union all table industry_associations) oa using (transaction_id)
        group by oa.entity_id, c.cycle, c.recipient_party
    )

    select organization_entity, cycle, recipient_party, count, amount
    from contribs_by_cycle

    union all

    select organization_entity, -1, recipient_party, sum(count) as count, sum(amount) as amount
    from contribs_by_cycle
    group by organization_entity, recipient_party
;

select date_trunc('second', now()) || ' -- create index agg_party_from_org_idx on agg_party_from_org (organization_entity, cycle)';
create index agg_party_from_org_idx on agg_party_from_org (organization_entity, cycle);



-- State/Fed from Organization


select date_trunc('second', now()) || ' -- drop table if exists agg_namespace_from_org';
drop table if exists agg_namespace_from_org cascade;

select date_trunc('second', now()) || ' -- create table agg_namespace_from_org';
create table agg_namespace_from_org as
    with contribs_by_cycle as (
        select oa.entity_id as organization_entity, c.cycle, c.transaction_namespace, count(*), sum(amount) as amount
        from contributions_all_relevant c
        inner join (table contributor_associations union table organization_associations union table parent_organization_associations union all table industry_associations) oa using (transaction_id)
        group by oa.entity_id, c.cycle, c.transaction_namespace
    )

    select organization_entity, cycle, transaction_namespace, count, amount
    from contribs_by_cycle

    union all

    select organization_entity, -1, transaction_namespace, sum(count) as count, sum(amount) as amount
    from contribs_by_cycle
    group by organization_entity, transaction_namespace
;

select date_trunc('second', now()) || ' -- create index agg_namespace_from_org_idx on agg_namespace_from_org (organization_entity, cycle)';
create index agg_namespace_from_org_idx on agg_namespace_from_org (organization_entity, cycle);

-- In-state/Out-of-state to Politician

select date_trunc('second', now()) || ' -- drop table if exists agg_local_to_politician';
drop table if exists agg_local_to_politician cascade;

select date_trunc('second', now()) || ' -- create table agg_local_to_politician';
create table agg_local_to_politician as
    with contribs_by_cycle as (
        select ra.entity_id as recipient_entity, c.cycle,
            case    when c.contributor_state = c.recipient_state then 'in-state'
                    when c.contributor_state = '' then ''
                    else 'out-of-state' end as local,
            count(*), sum(amount) as amount
        from contributions_individual c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, c.cycle,
            case    when c.contributor_state = c.recipient_state then 'in-state'
                    when c.contributor_state = '' then ''
                    else 'out-of-state' end
    )
    select recipient_entity, cycle, local, count, amount
    from contribs_by_cycle

    union all

    select recipient_entity, -1, local, sum(count) as count, sum(amount) amount
    from contribs_by_cycle
    group by recipient_entity, local;

select date_trunc('second', now()) || ' -- create index agg_local_to_politician_idx on agg_local_to_politician (recipient_entity, cycle)';
create index agg_local_to_politician_idx on agg_local_to_politician (recipient_entity, cycle);

-- In-state/Out-of-state from individual

select date_trunc('second', now()) || ' -- drop table if exists agg_local_from_indiv';
drop table if exists agg_local_from_indiv cascade;

select date_trunc('second', now()) || ' -- create table agg_local_from_indiv';
create table agg_local_from_indiv as
    with contribs_by_cycle as (
        select ca.entity_id as contributor_entity, c.cycle,
            case    when c.contributor_state = c.recipient_state then 'in-state'
                    when c.contributor_state = '' then ''
                    else 'out-of-state' end as local,
            count(*) as count, sum(amount) as amount
        from contributions_individual c
        inner join contributor_associations ca using (transaction_id)
        group by ca.entity_id, c.cycle,
            case    when c.contributor_state = c.recipient_state then 'in-state'
                    when c.contributor_state = '' then ''
                    else 'out-of-state' end
    )
    select contributor_entity, cycle, local, count, amount, 
            rank() over(partition by cycle, local order by count desc) as rank_by_count, 
            rank() over(partition by cycle, local order by amount desc) as rank_by_amount
    from contribs_by_cycle

    union all

    select contributor_entity, -1, local, sum(count) as count, sum(amount) amount,
            rank() over(partition by local order by sum(count) desc) as rank_by_count, 
            rank() over(partition by local order by sum(amount) desc) as rank_by_amount
        from contribs_by_cycle
    group by contributor_entity, local;

select date_trunc('second', now()) || ' -- create index agg_local_from_indiv_idx on agg_local_from_indiv (contributor_entity, cycle)';
create index agg_local_from_indiv_idx on agg_local_from_indiv (contributor_entity, cycle);


-- Indiv/PAC to Politician


select date_trunc('second', now()) || ' -- drop table if exists agg_contributor_type_to_politician';
drop table if exists agg_contributor_type_to_politician cascade;

select date_trunc('second', now()) || ' -- create table agg_contributor_type_to_politician';
create table agg_contributor_type_to_politician as
    with contribs_by_cycle as (
        select ra.entity_id as recipient_entity, c.cycle, coalesce(c.contributor_type, '') as contributor_type, count(*), sum(amount) as amount
        from (table contributions_individual union table contributions_organization) c
        inner join recipient_associations ra using (transaction_id)
        group by ra.entity_id, c.cycle, coalesce(c.contributor_type, '')
    )
    select recipient_entity, cycle, contributor_type, count, amount
    from contribs_by_cycle

    union all

    select recipient_entity, -1, contributor_type, sum(count) as count, sum(amount) as amount
    from contribs_by_cycle
    group by recipient_entity, contributor_type;

select date_trunc('second', now()) || ' -- create index agg_contributor_type_to_politician_idx on agg_contributor_type_to_politician (recipient_entity, cycle)';
create index agg_contributor_type_to_politician_idx on agg_contributor_type_to_politician (recipient_entity, cycle);

-- Top Orgs By Industry

select date_trunc('second', now()) || ' -- drop table if exists agg_top_orgs_by_industry';
drop table if exists agg_top_orgs_by_industry cascade;

select date_trunc('second', now()) || ' -- create table agg_top_orgs_by_industry';
create table agg_top_orgs_by_industry as
    with contribs_by_cycle as (
        select
            industry_entity, organization_name, organization_entity, cycle,
            coalesce(top_pacs.count, 0) + coalesce(top_indivs.count, 0) as total_count,
            coalesce(top_pacs.count, 0) as pacs_count,
            coalesce(top_indivs.count, 0) as indivs_count,
            coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0) as total_amount,
            coalesce(top_pacs.amount, 0) as pacs_amount,
            coalesce(top_indivs.amount, 0) as indivs_amount,
            rank() over (partition by industry_entity, cycle order by (coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0)) desc) as rank
        from (
                select
                    ia.entity_id as industry_entity,
                    coalesce(oe.name, c.contributor_name) as organization_name,
                    ca.entity_id as organization_entity,
                    c.cycle,
                    count(*),
                    sum(amount) as amount
                from
                    contributions_organization c -- organization contributions (PACs)
                    inner join industry_associations ia using (transaction_id) -- get the industry
                    left join organization_associations ca using (transaction_id) -- this is just the direct contributor (PAC)
                    left join matchbox_entity oe on oe.id = ca.entity_id -- get the entity associated with the contributor
                where coalesce(oe.name, c.contributor_name) != ''
                group by
                    ia.entity_id, coalesce(oe.name, c.contributor_name), ca.entity_id, c.cycle
            ) top_pacs
            full outer join (
                select
                    ia.entity_id as industry_entity,
                    coalesce(oe.name, c.organization_name) as organization_name,
                    oa.entity_id as organization_entity,
                    c.cycle,
                    count(*),
                    sum(amount) as amount
                from
                    (table contributions_individual union table contributions_individual_to_organization) c -- individual contributions
                    inner join industry_associations ia using (transaction_id) -- get the industry
                    left join organization_associations oa using (transaction_id) -- this is the org associated with the individual
                    left join matchbox_entity oe on oe.id = oa.entity_id -- get the entity associated with the org
                where coalesce(oe.name, c.organization_name) != ''
                group by
                    ia.entity_id, coalesce(oe.name, c.organization_name), oa.entity_id, c.cycle
            ) top_indivs
            using (industry_entity, organization_name, organization_entity, cycle)
    )
    select
        industry_entity, organization_name, organization_entity, cycle, total_count,
        pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from contribs_by_cycle
    where rank <= :agg_top_n

    union all

    select
        industry_entity, organization_name, organization_entity, -1, total_count,
        pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
    from (
        select
            industry_entity, organization_name, organization_entity,
            sum(total_count) as total_count,
            sum(pacs_count) as pacs_count,
            sum(indivs_count) as indivs_count,
            sum(total_amount) as total_amount,
            sum(pacs_amount) as pacs_amount,
            sum(indivs_amount) as indivs_amount,
            rank() over (partition by industry_entity order by sum(total_amount) desc) as rank
        from contribs_by_cycle
        group by industry_entity, organization_name, organization_entity
    ) x
    where rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_top_orgs_by_industry_idx on agg_top_orgs_by_industry (recipient_entity, cycle)';
create index agg_top_orgs_by_industry_idx on agg_top_orgs_by_industry (industry_entity, cycle);


select date_trunc('second', now()) || ' -- Finished computing contribution aggregates.';
