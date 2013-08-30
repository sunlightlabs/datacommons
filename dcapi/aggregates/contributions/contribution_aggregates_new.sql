-- Contributions to candidates from organizations and parent organizations 
-- (from agg_cand_from_org, changes indicated in comments)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals
-- test: join with agg_cands_from_org using (organization_entity, cycle, recipient_enity), check rank, counts, and amounts
select date_trunc('second', now()) || ' -- drop table if exists aggregate_candidates_from_organization';
drop table if exists aggregate_candidates_from_organization cascade;

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
                -- where coalesce(re.name, c.recipient_name) != ''
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

;

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
            
            union all

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
           
        select organization_entity, cycle, direct_or_indiv, count, amount 
            from
                pivoted_direct_indiv pdi
                    inner join
                matchbox_entity me on me.id = pdi.organization_entity; 

select date_trunc('second', now()) || ' -- create index aggregate_biggest_org_by_indiv_pac_cycle_rank_idx on aggregate_biggest_org_by_indiv_pac (cycle, organization_entity)';
create index aggregate_organizations_by_indiv_pac_cycle_rank_by_amount_idx on aggregate_organizations_by_indiv_pac (cycle, organization_entity);

-- Contributions to parties from organizations and parent organizations 
-- (to replace agg_party_from_org, total departure, based on aggregate_organizations_by...)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals, includes pacs and cands
-- test: join with agg_party_from_org using (organization_entity, cycle, recipient_party), check 
select date_trunc('second', now()) || ' -- drop table if exists aggregate_parties_from_organization';
drop table if exists aggregate_parties_from_organization cascade;

select date_trunc('second', now()) || ' -- create table aggregate_parties_from_organization';
create table aggregate_parties_from_organization as 
    with org_contributions_by_cycle as
        (select organization_entity, 
                recipient_party,  
                cycle,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by organization_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by organization_entity, cycle order by sum(amount) desc) as rank_by_amount
            from 
            
               ( select ca.entity_id as organization_entity, 
                       co.recipient_party,
                       cycle, 
                       count(*) as count, 
                       sum(co.amount) as amount
                from 
                    (table contributions_organization 
                     union table contributions_org_to_pac ) co
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations ) ca using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ca.entity_id, co.recipient_party, cycle

            union all

                select oa.entity_id as organization_entity, 
                       ci.recipient_party,
                       cycle, 
                       count(*) as count, 
                       sum(ci.amount) as amount
                from 
                    (table contributions_individual 
                     union table contributions_individual_to_organization) ci
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations ) oa using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by oa.entity_id, ci.recipient_party, cycle) x

            group by organization_entity, recipient_party, cycle
        )
    
    select  organization_entity, 
            recipient_party,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        org_contributions_by_cycle

    union all

    select  organization_entity, 
            recipient_party,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select organization_entity, 
                recipient_party,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by organization_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by organization_entity order by sum(amount) desc) as rank_by_amount
        from 
            org_contributions_by_cycle
        group by organization_entity, recipient_party
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_parties_from_organization_entity_cycle_idx on aggregate_parties_from_organization (organization_entity, cycle)';
create index aggregate_parties_from_organization_idx on aggregate_parties_from_organization (organization_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_parties_from_organization_party_cycle_idx on aggregate_parties_from_organization (recipient_party, cycle)';
create index aggregate_parties_from_organization_party_cycle_idx on aggregate_parties_from_organization (recipient_party, cycle);

-- Contributions to state and federal races from organizations and parent organizations 
-- (to replace agg_namespace_from_org, total departure, based on aggregate_organizations_by...)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals, includes pacs and cands
-- test: join with agg_party_from_org using (organization_entity, cycle, transaction_namespace), check 
select date_trunc('second', now()) || ' -- drop table if exists aggregate_state_fed_from_organization';
drop table if exists aggregate_state_fed_from_organization cascade;

select date_trunc('second', now()) || ' -- create table aggregate_state_fed_from_organization';
create table aggregate_state_fed_from_organization as 
    with org_contributions_by_cycle as
        (select organization_entity, 
                state_or_federal,  
                cycle,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by organization_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by organization_entity, cycle order by sum(amount) desc) as rank_by_amount
            from 
            
               ( select ca.entity_id as organization_entity, 
                       case when co.transaction_namespace = 'urn:fec:transaction' then 'federal' 
                            when co.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                            else 'other' end as state_or_federal,
                       -- ci.transaction_namespace,
                       cycle, 
                       count(*) as count, 
                       sum(co.amount) as amount
                from 
                    (table contributions_organization 
                     union table contributions_org_to_pac ) co
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations ) ca using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ca.entity_id, co.transaction_namespace, cycle

            union all

                select oa.entity_id as organization_entity, 
                       case when ci.transaction_namespace = 'urn:fec:transaction' then 'federal' 
                            when ci.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                            else 'other' end as state_or_federal,
                       -- ci.transaction_namespace,
                       cycle, 
                       count(*) as count, 
                       sum(ci.amount) as amount
                from 
                    (table contributions_individual 
                     union table contributions_individual_to_organization) ci
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations ) oa using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by oa.entity_id, ci.transaction_namespace, cycle) x

            group by organization_entity, state_or_federal, cycle
        )
    
    select  organization_entity, 
            state_or_federal,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        org_contributions_by_cycle

    union all

    select  organization_entity, 
            state_or_federal,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select organization_entity, 
                state_or_federal,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by organization_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by organization_entity order by sum(amount) desc) as rank_by_amount
        from 
            org_contributions_by_cycle
        group by organization_entity, transaction_namespace
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_state_fed_from_organization_entity_cycle_idx on aggregate_state_fed_from_organization (organization_entity, cycle)';
create index aggregate_state_fed_from_organization_idx on aggregate_state_fed_from_organization (organization_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_state_fed_from_organization_party_cycle_idx on aggregate_state_fed_from_organization (transaction_namespace, cycle)';
create index aggregate_state_fed_from_organization_state_or_federal_cycle_idx on aggregate_state_fed_from_organization (state_or_federal,cycle);

-- Contributions to state and federal races from organizations and parent organizations 
-- (to replace agg_namespace_from_org, total departure, based on aggregate_organizations_by...)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals, includes pacs and cands
-- test: join with agg_party_from_org using (organization_entity, cycle, transaction_namespace), check 
select date_trunc('second', now()) || ' -- drop table if exists aggregate_seat_from_organization';
drop table if exists aggregate_seat_from_organization cascade;

select date_trunc('second', now()) || ' -- create table aggregate_seat_from_organization';
create table aggregate_seat_from_organization as 
    with org_contributions_by_cycle as
        (select organization_entity, 
                seat,  
                cycle,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by organization_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by organization_entity, cycle order by sum(amount) desc) as rank_by_amount
            from 
            
               ( select ca.entity_id as organization_entity, 
                       co.seat,
                       cycle, 
                       count(*) as count, 
                       sum(co.amount) as amount
                from 
                    (table contributions_organization 
                     union table contributions_org_to_pac ) co
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations ) ca using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ca.entity_id, co.seat, cycle

            union all

                select oa.entity_id as organization_entity, 
                       ci.seat,
                       cycle, 
                       count(*) as count, 
                       sum(ci.amount) as amount
                from 
                    (table contributions_individual 
                     union table contributions_individual_to_organization) ci
                        inner join 
                    (table organization_associations 
                     union table parent_organization_associations ) oa using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by oa.entity_id, ci.seat, cycle) x

            group by organization_entity, seat, cycle
        )
    
    select  organization_entity, 
            seat,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        org_contributions_by_cycle

    union all

    select  organization_entity, 
            seat,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select organization_entity, 
                seat,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by organization_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by organization_entity order by sum(amount) desc) as rank_by_amount
        from 
            org_contributions_by_cycle
        group by organization_entity, seat
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_seat_from_organization_entity_cycle_idx on aggregate_seat_from_organization (organization_entity, cycle)';
create index aggregate_seat_from_organization_idx on aggregate_seat_from_organization (organization_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_seat_from_organization_seat_cycle_idx on aggregate_seat_from_organization (seat, cycle)';
create index aggregate_seat_from_organization_seat_cycle_idx on aggregate_seat_from_organization (seat, cycle);

---- INDIVIDUALS

-- Contributions to state and federal races from individuals 
-- to replace agg_namespace_from_indiv
-- difference: doesn't cut off at top 10, doesn't filter for recip party, contributor type or namespace explicity, includes pacs and cands
-- test: join with agg_namespace_from_indiv using (individual_entity, cycle, transaction_namespace), check 
select date_trunc('second', now()) || ' -- drop table if exists aggregate_state_fed_from_individual';
drop table if exists aggreggate_state_fed_from_individual cascade;

select date_trunc('second', now()) || ' -- create table aggregate_state_fed_from_individual';
create table aggregate_state_fed_from_individual as 
    with contributions_by_cycle as
        (select ca.entity_id as individual_entity, 
                       ci.transaction_namespace,
                       cycle, 
                       count(*) as count, 
                       sum(ci.amount) as amount,
                        rank() over (partition by ca.entity_id, cycle order by count(*) desc) as rank_by_count,
                        rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank_by_amount
                from 
                    (table contributions_individual   
                     union table contributions_individual_to_organization ) ci
                        inner join 
                    contributor_associations ca using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                    group by ca.entity_id, ci.transaction_namespace, cycle)
    
    select  individual_entity, 
            transaction_namespace,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        contributions_by_cycle

    union all

    select  individual_entity, 
            transaction_namespace,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select individual_entity, 
                transaction_namespace,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by individual_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by individual_entity order by sum(amount) desc) as rank_by_amount
        from 
            contributions_by_cycle
        group by individual_entity, transaction_namespace
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_state_fed_from_individual_entity_cycle_idx on aggregate_state_fed_from_individual (individual_entity, cycle)';
create index aggregate_state_fed_from_individual_idx on aggregate_state_fed_from_individual (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_state_fed_from_individual_party_cycle_idx on aggregate_state_fed_from_individual (transaction_namespace, cycle)';
create index aggregate_state_fed_from_individual_state_fed_cycle_idx on aggregate_state_fed_from_individual (transaction_namespace, cycle);

-- Contributions to state and federal races from individuals 
-- to replace agg_party_from_indiv
-- difference: doesn't cut off at top 10, doesn't filter for recip party, contributor type or namespace explicity, includes pacs and cands
-- test: join with agg_party_from_indiv using (individual_entity, cycle, transaction_namespace), check 
select date_trunc('second', now()) || ' -- drop table if exists aggregate_party_from_individual';
drop table if exists aggreggate_party_from_individual cascade;

select date_trunc('second', now()) || ' -- create table aggregate_party_from_individual';
create table aggregate_party_from_individual as 
    with contributions_by_cycle as
        (select ca.entity_id as individual_entity, 
                       ci.recipient_party,
                       cycle, 
                       count(*) as count, 
                       sum(ci.amount) as amount,
                        rank() over (partition by ci.entity, cycle order by count(*) desc) as rank_by_count,
                        rank() over (partition by ci.entity, cycle order by sum(ci.amount) desc) as rank_by_amount
                from 
                    (table contributions_individual   
                     union table contributions_individual_to_organization ) ci
                        inner join 
                    contributor_associations ca using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                    group by ca.entity_id, ci.transaction_namespace, cycle)
    
    select  individual_entity, 
            recipient_party,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        contributions_by_cycle

    union all

    select  individual_entity, 
            recipient_party,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select individual_entity, 
                    recipient_party,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by individual_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by individual_entity order by sum(amount) desc) as rank_by_amount
        from 
            contributions_by_cycle
        group by individual_entity, transaction_namespace
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_recipient_party_from_individual_entity_cycle_idx on aggregate_recipient_party_from_individual (individual_entity, cycle)';
create index aggregate_recipient_party_from_individual_idx on aggregate_recipient_party_from_individual (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_recipient_party_from_individual_party_cycle_idx on aggregate_state_fed_from_individual (transaction_namespace, cycle)';
create index aggregate_recipient_party_from_individual_party_cycle_idx on aggregate_recipient_party_from_individual (recipient_party, cycle);

-- Contributions to in state and out of state policitians from individuals 
-- to replace agg_in_state_out_of_state_from_indiv
-- difference: doesn't cut off at top 10, doesn't filter for recip party, contributor type or namespace explicity, includes pacs and cands
-- test: join with agg_party_from_indiv using (individual_entity, cycle, transaction_namespace), check 
select date_trunc('second', now()) || ' -- drop table if exists aggregate_state_fed_from_individual';
drop table if exists aggreggate_in_state_out_of_state_from_individual cascade;

select date_trunc('second', now()) || ' -- create table aggregate_state_fed_from_individual';
create table aggregate_in_state_out_of_state_from_individual as 
    with contributions_by_cycle as
        (select individual_entity, 
                in_state_out_of_state,
                cycle,
                count(*) as count, 
                sum(amount) as amount,
                rank() over (partition by individual_entity, cycle order by count(*) desc) as rank_by_count,
                rank() over (partition by individual_entity, cycle order by sum(amount) desc) as rank_by_amount
                from
                    (select ca.entity_id as individual_entity, 
                                case    when ci.contributor_state = ci.recipient_state then 'in-state'
                                        when ci.contributor_state = '' then ''
                                        else 'out-of-state' end as in_state_out_of_state,
                                   cycle,
                                   amount
                            from 
                                contributions_individual ci
                                    inner join 
                                contributor_associations ca using (transaction_id)
                                    left join 
                                recipient_associations ra using (transaction_id)
                                    left join 
                                matchbox_entity re on re.id = ra.entity_id
                    ) x
                group by individual_entity, in_state_out_of_state, cycle)
    
    select  individual_entity, 
            in_state_out_of_state,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        contributions_by_cycle

    union all

    select  individual_entity, 
            in_state_out_of_state,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select individual_entity, 
                in_state_out_of_state,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by individual_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by individual_entity order by sum(amount) desc) as rank_by_amount
        from 
            contributions_by_cycle
        group by individual_entity, transaction_namespace
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_recipient_in_state_out_of_state_from_individual_entity_cycle_idx on aggregate_recipient_in_state_out_of_state_from_individual (individual_entity, cycle)';
create index aggregate_recipient_in_state_out_of_state_from_individual_idx on aggregate_recipient_in_state_out_of_state_from_individual (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_in_state_out_of_state_from_individual_in_state_out_of_state_cycle_idx on aggregate_in_state_out_of_state_from_individual (in_state_out_of_state, cycle)';
create index aggregate_in_state_out_of_state_from_individual_in_state_out_of_state_cycle_idx on aggregate_in_state_out_of_state_from_individual (in_state_out_of_state, cycle);

---- INDUSTRIES


-- Contributions to candidates from industries
select date_trunc('second', now()) || ' -- drop table if exists aggregate_candidates_from_industry';
drop table if exists aggregate_candidates_from_industry cascade;

select date_trunc('second', now()) || ' -- create table aggregate_candidates_from_industry';
create table aggregate_candidates_from_industry as 
    with contributions_by_cycle as
        (select industry_entity, 
                recipient_name, 
                recipient_entity, 
                cycle,
                coalesce(direct.count, 0) + coalesce(indivs.count, 0) as total_count,
                coalesce(direct.count, 0) as pacs_count,
                coalesce(indivs.count, 0) as indivs_count,
                coalesce(direct.amount, 0) + coalesce(indivs.amount, 0) as total_amount,
                coalesce(direct.amount, 0) as pacs_amount,
                coalesce(indivs.amount, 0) as indivs_amount,
                rank() over (partition by industry_entity, cycle order by (coalesce(direct.amount, 0) + coalesce(indivs.amount, 0)) desc) as rank
            from 
                (
                select ia.entity_id as industry_entity, 
                       coalesce(re.name, co.recipient_name) as recipient_name, 
                       ra.entity_id as recipient_entity,
                       cycle, 
                       count(*), 
                       sum(co.amount) as amount
                from contributions_organization co
                        inner join 
                    industry_associations ia using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ia.entity_id, coalesce(re.name, co.recipient_name), ra.entity_id, cycle
                )  direct
            full outer join 
                (
                select  ia.entity_id as industry_entity, 
                        coalesce(re.name, ci.recipient_name) as recipient_name, 
                        ra.entity_id as recipient_entity,
                        cycle, 
                        count(*), 
                        sum(amount) as amount
                from 
                    contributions_individual ci
                        inner join 
                    industry_associations ia using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ia.entity_id, coalesce(re.name, ci.recipient_name), ra.entity_id, cycle
                ) indivs 
        using (industry_entity, recipient_name, recipient_entity, cycle)
    )
    
    select  industry_entity, 
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
        contributions_by_cycle

    union all

    select 
            industry_entity, 
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
                industry_entity, 
                recipient_name, 
                recipient_entity,
                sum(total_count) as total_count, 
                sum(pacs_count) as pacs_count, 
                sum(indivs_count) as indivs_count,
                sum(total_amount) as total_amount, 
                sum(pacs_amount) as pacs_amount, 
                sum(indivs_amount) as indivs_amount,
                rank() over (partition by industry_entity order by sum(total_amount) desc) as rank
        from 
            contributions_by_cycle
        group by industry_entity, recipient_name, recipient_entity
        ) all_cycle_rollup 

;

select date_trunc('second', now()) || ' -- create index aggregate_candidates_from_industry_idx on aggregate_candidates_from_industry (industry_entity, cycle)';
create index aggregate_candidates_from_industry_idx on aggregate_candidates_from_industry (industry_entity, cycle);

-- Contributions to candidates from industries
select date_trunc('second', now()) || ' -- drop table if exists aggregate_candidates_from_industry';
drop table if exists aggregate_pacs_from_industry cascade;

select date_trunc('second', now()) || ' -- create table aggregate_candidates_from_industry';
create table aggregate_pacs_from_industry as 
    with contributions_by_cycle as
        (select industry_entity, 
                recipient_name, 
                recipient_entity, 
                cycle,
                coalesce(direct.count, 0) + coalesce(indivs.count, 0) as total_count,
                coalesce(direct.count, 0) as pacs_count,
                coalesce(indivs.count, 0) as indivs_count,
                coalesce(direct.amount, 0) + coalesce(indivs.amount, 0) as total_amount,
                coalesce(direct.amount, 0) as pacs_amount,
                coalesce(indivs.amount, 0) as indivs_amount,
                rank() over (partition by industry_entity, cycle order by (coalesce(direct.amount, 0) + coalesce(indivs.amount, 0)) desc) as rank
            from 
                (
                select ia.entity_id as industry_entity, 
                       coalesce(re.name, c.recipient_name) as recipient_name, 
                       ra.entity_id as recipient_entity,
                       cycle, 
                       count(*), 
                       sum(c.amount) as amount
                from contributions_org_to_pac c
                        inner join 
                    industry_associations ia using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ia.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
                )  direct
            full outer join 
                (
                select  ia.entity_id as industry_entity, 
                        coalesce(re.name, c.recipient_name) as recipient_name, 
                        ra.entity_id as recipient_entity,
                        cycle, 
                        count(*), 
                        sum(amount) as amount
                from 
                    contributions_individual_to_organization c
                        inner join 
                    industry_associations ia using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ia.entity_id, coalesce(re.name, c.recipient_name), ra.entity_id, cycle
                ) indivs 
        using (industry_entity, recipient_name, recipient_entity, cycle)
    )
    
    select  industry_entity, 
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
        contributions_by_cycle

    union all

    select 
            industry_entity, 
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
                industry_entity, 
                recipient_name, 
                recipient_entity,
                sum(total_count) as total_count, 
                sum(pacs_count) as pacs_count, 
                sum(indivs_count) as indivs_count,
                sum(total_amount) as total_amount, 
                sum(pacs_amount) as pacs_amount, 
                sum(indivs_amount) as indivs_amount,
                rank() over (partition by industry_entity order by sum(total_amount) desc) as rank
        from 
            contributions_by_cycle
        group by industry_entity, recipient_name, recipient_entity
        ) all_cycle_rollup 

;

select date_trunc('second', now()) || ' -- create index aggregate_candidates_from_industry_idx on aggregate_candidates_from_industry (industry_entity, cycle)';
create index aggregate_pacs_from_industry_idx on aggregate_pacs_from_industry (industry_entity, cycle);

-- CONTRIBUTIONS FROM ORGS BY ASSOCIATED INDIV/PAC
select date_trunc('second', now()) || ' -- drop table if exists aggregate_industries_by_indiv_pac';
drop table if exists aggregate_industries_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table aggregate_industries_by_indiv_pac';
create table aggregate_industries_by_indiv_pac as
    with contributions_by_cycle as 
        (select 
            industry_entity,
            cycle,
            sum(pacs_count) as pacs_count,
            sum(pacs_amount) as pacs_amount,
            sum(indivs_count) as indivs_count,
            sum(indivs_amount) as indivs_amount
            from
                (table aggregate_candidates_from_industry
                 union table aggregate_pacs_from_industry) as aggs
        group by industry_entity, cycle),
    pivoted_direct_indiv as 
        (select
            industry_entity,
            cycle,
            direct_or_indiv,
            count, 
            amount
            from
            (select 
                industry_entity,
                cycle,
                'direct' as direct_or_indiv,
                pacs_count as count, 
                pacs_amount as amount
                from
                    contributions_by_cycle cbc
                        inner join
                    matchbox_entity me on me.id = cbc.industry_entity
            
            union all

            select 
                industry_entity,
                cycle,
                'indiv' as direct_or_indiv,
                indivs_count as count, 
                indivs_amount as amount
                from
                    contributions_by_cycle cbc
                        inner join
                    matchbox_entity me on me.id = cbc.industry_entity) x)
           
        select industry_entity, cycle, direct_or_indiv, count, amount 
            from
                pivoted_direct_indiv pdi
                    inner join
                matchbox_entity me on me.id = pdi.industry_entity; 

select date_trunc('second', now()) || ' -- create index aggregate_industries_by_indiv_pac_cycle_rank_idx on aggregate_industries_by_indiv_pac (cycle, organization_entity)';
create index aggregate_industries_by_indiv_pac_cycle_rank_by_amount_idx on aggregate_industries_by_indiv_pac (cycle, industry_entity);

-- Contributions to parties from industry 
select date_trunc('second', now()) || ' -- drop table if exists aggregate_parties_from_industry';
drop table if exists aggreggate_parties_from_industry cascade;

select date_trunc('second', now()) || ' -- create table aggregate_parties_from_industry';
create table aggregate_parties_from_industry as 
    with contributions_by_cycle as
        (select industry_entity, 
                recipient_party,  
                cycle,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by industry_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by industry_entity, cycle order by sum(amount) desc) as rank_by_amount
            from 
            
               ( select co.entity_id as industry_entity, 
                       co.recipient_party,
                       cycle, 
                       count(*) as count, 
                       sum(co.amount) as amount
                from 
                    (table contributions_organization 
                     union table contributions_org_to_pac ) co
                        inner join 
                    industry_associations ia using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by co.entity_id, co.recipient_party, cycle

            union all

                select ci.entity_id as industry_entity, 
                       ci.recipient_party,
                       cycle, 
                       count(*) as count, 
                       sum(ci.amount) as amount
                from 
                    (table contributions_individual 
                     union table contributions_individual_to_organization) ci
                        inner join 
                    industry_associations ia using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by ci.entity_id, ci.recipient_party, cycle) x

            group by organization_entity, recipient_party, cycle
        )
    
    select  industry_entity, 
            recipient_party,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        contributions_by_cycle

    union all

    select  industry_entity, 
            recipient_party,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select industry_entity, 
                recipient_party,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by industry_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by industry_entity order by sum(amount) desc) as rank_by_amount
        from 
            contributions_by_cycle
        group by industry_entity, recipient_party
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_parties_from_industry_entity_cycle_idx on aggregate_parties_from_industry (organization_entity, cycle)';
create index aggregate_parties_from_industry_idx on aggregate_parties_from_industry (industry_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_parties_from_industry_party_cycle_idx on aggregate_parties_from_industry (recipient_party, cycle)';
create index aggregate_parties_from_industry_party_cycle_idx on aggregate_parties_from_industry (recipient_party, cycle);



-- Contributions to state and federal races from industries
select date_trunc('second', now()) || ' -- drop table if exists aggregate_state_fed_from_organization';
drop table if exists aggreggate_state_fed_from_industry cascade;

select date_trunc('second', now()) || ' -- create table aggregate_state_fed_from_organization';
create table aggregate_state_fed_from_industry as 
    with contributions_by_cycle as
        (select industry_entity, 
                state_or_federal,  
                cycle,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by industry_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by industry_entity, cycle order by sum(amount) desc) as rank_by_amount
            from 
            (
                select ia.entity_id as industry_entity, 
                           case when co.transaction_namespace = 'urn:fec:transaction' then 'federal' 
                                when co.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                                else 'other' end as state_or_federal,
                           cycle,  
                           co.amount
                    from 
                        (table contributions_organization 
                         union table contributions_org_to_pac ) co
                            inner join 
                        industry_associations ia using (transaction_id)
                            left join 
                        recipient_associations ra using (transaction_id)
                            left join 
                        matchbox_entity re on re.id = ra.entity_id
                    group by industry_entity, co.transaction_namespace, cycle

            union all

                select ia.entity_id as industry_entity, 
                           case when ci.transaction_namespace = 'urn:fec:transaction' then 'federal' 
                                when ci.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                                else 'other' end as state_or_federal,
                           cycle,  
                           co.amount
                from 
                    (table contributions_individual 
                     union table contributions_individual_to_organization) ci
                        inner join 
                    industry_associations ia using (transaction_id)
                        left join 
                    recipient_associations ra using (transaction_id)
                        left join 
                    matchbox_entity re on re.id = ra.entity_id
                group by oa.entity_id, ci.transaction_namespace, cycle
            ) x

            group by organization_entity, state_or_federal, cycle
        )
    
    select  industry_entity, 
            state_or_federal,  
            cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        contributions_by_cycle

    union all

    select  industry_entity, 
            state_or_federal,  
            -1 as cycle,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from 
        (select industry_entity, 
                state_or_federal,  
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by state_or_federal order by sum(count) desc) as rank_by_count,
                rank() over(partition by state_or_federal order by sum(amount) desc) as rank_by_amount
        from 
            contributions_by_cycle
        group by industry_entity, recipient_party
        ) all_cycle_rollup 
;

select date_trunc('second', now()) || ' -- create index aggregate_state_fed_from_industry_entity_cycle_idx on aggregate_state_fed_from_industry (organization_entity, cycle)';
create index aggregate_state_fed_from_industry_idx on aggregate_state_fed_from_industry (industry_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_state_fed_from_industry_party_cycle_idx on aggregate_state_fed_from_industry (recipient_party, cycle)';
create index aggregate_state_fed_from_industry_state_fed_cycle_idx on aggregate_state_fed_from_industry (state_fed, cycle);


