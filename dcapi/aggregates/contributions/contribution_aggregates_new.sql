-- Contributions to candidates from organizations and parent organizations 
-- (from agg_cand_from_org, changes indicated in comments)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals
-- test: join with agg_cand_from_org using (organization_entity, cycle, recipient_enity), check rank, counts, and amounts
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


