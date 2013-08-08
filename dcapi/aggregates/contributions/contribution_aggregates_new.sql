-- Contributions to candidates from organizations and parent organizations 
-- (from agg_cand_from_org, changes indicated in comments)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals
-- test: join with agg_cands_from_org using (organization_entity, cycle, recipient_enity), check rank, counts, and amounts
select date_trunc('second', now()) || ' -- drop table if exists aggregate_candidates_from_organization';
drop table if exists aggreggate_candidates_from_organization cascade;

select date_trunc('second', now()) || ' -- create table aggregate_candidates_from_organization';
create table aggregate_candidates_from_organization as 
    with org_contributions_by_cycle as
        (select organization_entity, 
                recipient_name, 
                recipient_entity, 
                cycle,
                coalesce(direct.count, 0) + coalesce(indivs.count, 0) as total_count,
                coalesce(direct.count, 0) as pacs_count,
                coalesce(indivs.count, 0) as indivs_count,
                coalesce(direct.amount, 0) + coalesce(indivs.amount, 0) as total_amount,
                coalesce(direct.amount, 0) as pacs_amount,
                coalesce(indivs.amount, 0) as indivs_amount,
                rank() over (partition by organization_entity, cycle order by (coalesce(direct.amount, 0) + coalesce(indivs.amount, 0)) desc) as rank
            from 
                (
                select ca.entity_id as organization_entity, 
                       coalesce(re.name, c.recipient_name) as recipient_name, 
                       ra.entity_id as recipient_entity,
                       cycle, 
                       count(*), 
                       sum(c.amount) as amount
                from contributions_organization c
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations 
                                                             ) ca using (transaction_id)
                     -- union all table industry_associations) ca using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                where coalesce(re.name, c.recipient_name) != ''
                group by ca.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
                )  direct
            full outer join 
                (
                select  oa.entity_id as organization_entity, 
                        coalesce(re.name, c.recipient_name) as recipient_name, 
                        ra.entity_id as recipient_entity,
                        cycle, 
                        count(*), 
                        sum(amount) as amount
                from 
                    contributions_individual c
                        inner join 
                    -- (table contributor_associations 
                    --  union 
                    (table organization_associations 
                     union table parent_organization_associations 
                                                            ) oa using (transaction_id)
                     -- union all table industry_associations) oa using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by oa.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
                ) indivs 
        using (organization_entity, recipient_name, recipient_entity, cycle)
    )
    
    select  organization_entity, 
            recipient_name, 
            recipient_entity, 
            cycle,
            total_count, 
            pacs_count, 
            indivs_count, 
            total_amount, 
            pacs_amount, 
            indivs_amount,
            rank
    from 
        org_contributions_by_cycle

    union all

    select 
            organization_entity, 
            recipient_name, 
            recipient_entity, 
            -1 as cycle,
            total_count, 
            pacs_count, 
            indivs_count, 
            total_amount, 
            pacs_amount, 
            indivs_amount,
            rank
    from 
        (select 
                organization_entity, 
                recipient_name, 
                recipient_entity,
                sum(total_count) as total_count, 
                sum(pacs_count) as pacs_count, 
                sum(indivs_count) as indivs_count,
                sum(total_amount) as total_amount, 
                sum(pacs_amount) as pacs_amount, 
                sum(indivs_amount) as indivs_amount,
                rank() over (partition by organization_entity order by sum(total_amount) desc) as rank
        from 
            org_contributions_by_cycle
        group by organization_entity, recipient_name, recipient_entity
        ) all_cycle_rollup 

select date_trunc('second', now()) || ' -- create index aggregate_candidates_from_organization_idx on aggregate_candidates_from_organization (organization_entity, cycle)';
create index aggregate_candidates_from_organization_idx on aggregate_candidates_from_organization (organization_entity, cycle);

-- Contributions to pacs from organizations and parent organizations 
-- (from agg_pacs_from_org, changes indicated in comments)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals
-- test: join with agg_pacs_from_org using (organization_entity, cycle, recipient_enity), check rank, counts, and amounts

select date_trunc('second', now()) || ' -- drop table if exists aggregate_pacs_from_organization';
drop table if exists aggregate_pacs_from_organization cascade;

select date_trunc('second', now()) || ' -- create table aggregate_pacs_from_organization';
create table aggregate_pacs_from_organization as
    with org_contributions_by_cycle as 
        (select organization_entity, 
                recipient_name, 
                recipient_entity, 
                cycle,
                coalesce(direct.count, 0) + coalesce(indivs.count, 0) as total_count,
                coalesce(direct.count, 0) as pacs_count,
                coalesce(indivs.count, 0) as indivs_count,
                coalesce(direct.amount, 0) + coalesce(indivs.amount, 0) as total_amount,
                coalesce(direct.amount, 0) as pacs_amount,
                coalesce(indivs.amount, 0) as indivs_amount,
                rank() over (partition by organization_entity, cycle order by (coalesce(direct.amount, 0) + coalesce(indivs.amount, 0)) desc) as rank
            from 
                (
                select 
                    ca.entity_id as organization_entity, 
                    coalesce(re.name, c.recipient_name) as recipient_name, 
                    ra.entity_id as recipient_entity,
                    cycle, 
                    count(*), 
                    sum(c.amount) as amount
                from 
                    contributions_org_to_pac c
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations 
                                                          ) ca using (transaction_id)
                     -- union all table industry_associations) ca using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ca.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
                ) direct
            full outer join 
                (
                select 
                    oa.entity_id as organization_entity, 
                    coalesce(re.name, c.recipient_name) as recipient_name, 
                    ra.entity_id as recipient_entity,
                    cycle, 
                    count(*), 
                    sum(amount) as amount
                from 
                    contributions_individual_to_organization c
                        inner join 
                    -- (table contributor_associations
                    -- union
                    (table organization_associations
                    union table parent_organization_associations
                                                        ) oa using (transaction_id)
                    -- union all table industry_associations) oa using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by oa.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
            ) indivs using (organization_entity, recipient_name, recipient_entity, cycle)
        )
        

    select  organization_entity, 
            recipient_name, 
            recipient_entity, 
            cycle,
            total_count, 
            pacs_count, 
            indivs_count, 
            total_amount, 
            pacs_amount, 
            indivs_amount,
            rank
        from 
            org_contributions_by_cycle

    union all

    select  organization_entity,
            recipient_name, 
            recipient_entity, 
            -1 as cycle,
            total_count,
            pacs_count, 
            indivs_count, 
            total_amount, 
            pacs_amount, 
            indivs_amount,
            rank
        from 
        (select     organization_entity, 
                    recipient_name, 
                    recipient_entity,
                    sum(total_count) as total_count, 
                    sum(pacs_count) as pacs_count, 
                    sum(indivs_count) as indivs_count,
                    sum(total_amount) as total_amount, 
                    sum(pacs_amount) as pacs_amount, 
                    sum(indivs_amount) as indivs_amount,
                    rank() over (partition by organization_entity order by sum(total_amount) desc) as rank
            from 
                org_contributions_by_cycle
            group by organization_entity, recipient_name, recipient_entity
        ) all_cycle_rollup
    ;

select date_trunc('second', now()) || ' -- create index aggregate_pacs_from_organization_idx on aggregate_pacs_from_organization (organization_entity, cycle)';
create index aggregate_pacs_from_organization_idx on aggregate_pacs_from_organization (organization_entity, cycle);



-- CONTRIBUTIONS FROM ORGS BY ASSOCIATED INDIV/PAC
select date_trunc('second', now()) || ' -- drop table if exists aggregate_organizations_by_indiv_pac';
drop table if exists aggregate_organizations_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table aggregate_organizations_by_indiv_pac';
create table aggregate_organizations_by_indiv_pac as
    with contributions_by_cycle as 
        (select 
            organization_entity,
            cycle,
            sum(pacs_count) as pacs_count,
            sum(pacs_amount) as pacs_amount,
            sum(indivs_count) as indivs_count,
            sum(indivs_amount) as indivs_amount
            from
                (table aggregate_candidates_from_organization
                 union table aggregate_pacs_from_organization) as aggs
        group by organization_entity, cycle),
    pivoted_direct_indiv as 
        (select
            organization_entity,
            cycle,
            direct_or_indiv,
            count, 
            amount
            from
            (select
                organization_entity,
                cycle,
                'direct' as direct_or_indiv,
                pacs_count as count, 
                pacs_amount as amount
                from
                    contributions_by_cycle cbc
                        inner join
                    matchbox_entity me on me.id = cbc.organization_entity
            
            union

            select 
                organization_entity,
                cycle,
                'indiv' as direct_or_indiv,
                indivs_count as count, 
                indivs_amount as amount
                from
                    contributions_by_cycle cbc
                        inner join
                    matchbox_entity me on me.id = cbc.organization_entity) x)
           
        select me.name, organization_entity, cycle, direct_or_indiv, count, amount 
            from
                pivoted_direct_indiv pdi
                    inner join
                matchbox_entity me on me.id = pdi.organization_entity

        union

        select me.name, organization_entity, -1 as cycle, direct_or_indiv, sum(count) as count, sum(amount) as amount
            from
                pivoted_direct_indiv pdi
                    inner join
                matchbox_entity me on me.id = pdi.organization_entity
            group by organization_entity, direct_or_indiv, me.name;
                

select date_trunc('second', now()) || ' -- create index aggregate_biggest_org_by_indiv_pac_cycle_rank_idx on aggregate_biggest_org_by_indiv_pac (cycle, organization_entity)';
create index aggregate_organizations_by_indiv_pac_cycle_rank_by_amount_idx on aggregate_organizations_by_indiv_pac (cycle, organization_entity);
