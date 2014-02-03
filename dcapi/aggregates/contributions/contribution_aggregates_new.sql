-- Contributions to candidates from organizations and parent organizations
-- (from agg_cand_from_org, changes indicated in comments)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals
-- test: join with agg_cands_from_org using (organization_entity, cycle, recipient_enity), check rank, counts, and amounts
-- TODO: redo
-- SELECT 7144809
-- Time: 528774.054 ms
-- CREATE INDEX
-- Time: 17667.739 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_organization_to_candidates';
drop table if exists aggregate_organization_to_candidates cascade;

select date_trunc('second', now()) || ' -- create table aggregate_organization_to_candidates';
create table aggregate_organization_to_candidates as
    with org_contributions_by_cycle as
        (select organization_entity,
                cycle,
                recipient_name,
                recipient_entity,
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
                       cycle,
                       coalesce(re.name, c.recipient_name) as recipient_name,
                       ra.entity_id as recipient_entity,
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
                group by ca.entity_id, cycle, ra.entity, coalesce(re.name, c.recipient_name)
                )  direct
            full outer join
                (
                select  oa.entity_id as organization_entity,
                        cycle,
                        coalesce(re.name, c.recipient_name) as recipient_name,
                        ra.entity_id as recipient_entity,
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
                group by oa.entity_id, cycle, ra.entity, coalesce(re.name, c.recipient_name)
                ) indivs
        using (organization_entity, cycle, recipient_entity, recipient_name)
    )

    select  
            organization_entity,
            cycle,
            recipient_name,
            recipient_entity,
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
            -1 as cycle,
            recipient_name,
            recipient_entity,
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
        group by organization_entity, recipient_entity, recipient_name
        ) all_cycle_rollup

;

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_candidates_idx on aggregate_organization_to_candidates (organization_entity, cycle)';
create index aggregate_organization_to_candidates_idx on aggregate_organization_to_candidates (organization_entity, cycle);

-- Contributions to pacs from organizations and parent organizations
-- (from agg_pacs_from_org, changes indicated in comments)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals
-- test: join with agg_pacs_from_org using (organization_entity, cycle, recipient_enity), check rank, counts, and amounts
-- TODO: redo
-- SELECT 900946
-- Time: 340554.612 ms
-- CREATE INDEX
-- Time: 2151.247 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_organization_to_pacs';
drop table if exists aggregate_organization_to_pacs cascade;

select date_trunc('second', now()) || ' -- create table aggregate_organization_to_pacs';
create table aggregate_organization_to_pacs as
    with org_contributions_by_cycle as
        (
          select organization_entity,
                cycle,
                recipient_name,
                recipient_entity,
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
                    cycle,
                    coalesce(re.name, c.recipient_name) as recipient_name,
                    ra.entity_id as recipient_entity,
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
                group by ca.entity_id, cycle, ra.entity_id, coalesce(re.name, c.recipient_name)
                ) direct
            full outer join
                (
                select
                    oa.entity_id as organization_entity,
                    cycle,
                    coalesce(re.name, c.recipient_name) as recipient_name,
                    ra.entity_id as recipient_entity,
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
                group by oa.entity_id, cycle, ra.entity_id, coalesce(re.name, c.recipient_name)
            ) indivs using (organization_entity, cycle, recipient_entity, recipient_name)
        )

    select  organization_entity,
            cycle,
            recipient_name,
            recipient_entity,
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
            -1 as cycle,
            recipient_name,
            recipient_entity,
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
            group by organization_entity, recipient_entity, recipient_name
        ) all_cycle_rollup
    ;

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_pacs_idx on aggregate_organization_to_pacs (organization_entity, cycle)';
create index aggregate_organization_to_pacs_idx on aggregate_organization_to_pacs (organization_entity, cycle);



-- CONTRIBUTIONS FROM ORGS BY ASSOCIATED INDIV/PAC
-- debug: pass
-- SELECT 464018
-- Time: 46259.089 ms
-- CREATE INDEX
-- Time: 1166.399 ms


select date_trunc('second', now()) || ' -- drop table if exists aggregate_organization_by_indiv_pac';
drop table if exists aggregate_organization_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table aggregate_organization_by_indiv_pac';
create table aggregate_organization_by_indiv_pac as
    with contributions_by_cycle as
        (select
            organization_entity,
            cycle,
            sum(pacs_count) as pacs_count,
            sum(pacs_amount) as pacs_amount,
            sum(indivs_count) as indivs_count,
            sum(indivs_amount) as indivs_amount
            from
                (table aggregate_organization_to_candidates
                 union table aggregate_organization_to_pacs) as aggs
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

select date_trunc('second', now()) || ' -- create index aggregate_organization_by_indiv_pac_cycle_org_entity_idx on aggregate_organization_by_indiv_pac (cycle, organization_entity)';
create index aggregate_organization_by_indiv_pac_cycle_org_entity_idx on aggregate_organization_by_indiv_pac (cycle, organization_entity);

-- Contributions to parties from organizations and parent organizations
-- (to replace agg_party_from_org, total departure, based on aggregate_organizations_by...)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals, includes pacs and cands
-- test: join with agg_party_from_org using (organization_entity, cycle, recipient_party), check
-- debug: none
-- SELECT 422216
-- Time: 1688073.812 ms
-- CREATE INDEX
-- Time: 948.270 ms
-- CREATE INDEX
-- Time: 2352.049 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_organization_to_parties';
drop table if exists aggregate_organization_to_parties cascade;

select date_trunc('second', now()) || ' -- create table aggregate_organization_to_parties';
create table aggregate_organization_to_parties as
    with org_contributions_by_cycle as
        (select organization_entity,
                cycle,
                recipient_party,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by organization_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by organization_entity, cycle order by sum(amount) desc) as rank_by_amount
            from

               ( select ca.entity_id as organization_entity,
                       cycle,
                       co.recipient_party,
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
                group by ca.entity_id, cycle, co.recipient_party

            union all

                select oa.entity_id as organization_entity,
                       cycle,
                       ci.recipient_party,
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
                group by oa.entity_id, cycle, ci.recipient_party) x

            group by organization_entity, cycle, recipient_party
        )

    select  organization_entity,
            cycle,
            recipient_party,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        org_contributions_by_cycle

    union all

    select  organization_entity,
            -1 as cycle,
            recipient_party,
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

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_parties_entity_cycle_idx on aggregate_organization_to_parties (organization_entity, cycle)';
create index aggregate_organization_to_parties_idx on aggregate_organization_to_parties (organization_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_parties_party_cycle_idx on aggregate_organization_to_parties (recipient_party, cycle)';
create index aggregate_organization_to_parties_party_cycle_idx on aggregate_organization_to_parties (recipient_party, cycle);

-- Contributions to state and federal races from organizations and parent organizations
-- (to replace agg_namespace_from_org, total departure, based on aggregate_organizations_by...)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals, includes pacs and cands
-- test: join with agg_party_from_org using (organization_entity, cycle, transaction_namespace), check
-- 
-- SELECT 289894
-- Time: 1705866.352 ms
-- CREATE INDEX
-- Time: 707.513 ms
-- CREATE INDEX
-- Time: 3617.874 ms


select date_trunc('second', now()) || ' -- drop table if exists aggregate_organization_to_state_fed';
drop table if exists aggregate_organization_to_state_fed cascade;

select date_trunc('second', now()) || ' -- create table aggregate_organization_to_state_fed';
create table aggregate_organization_to_state_fed as
    with org_contributions_by_cycle as
        (select organization_entity,
                cycle,
                state_or_federal,
                count(*) as count,
                sum(amount) as amount,
                rank() over (partition by organization_entity, cycle order by count(*) desc) as rank_by_count,
                rank() over (partition by organization_entity, cycle order by sum(amount) desc) as rank_by_amount
            from

               ( select ca.entity_id as organization_entity,
                       cycle,
                       case when co.transaction_namespace = 'urn:fec:transaction' then 'federal'
                            when co.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                            else 'other' end as state_or_federal,
                       -- ci.transaction_namespace,
                       amount
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

            union all

                select oa.entity_id as organization_entity,
                       cycle,
                       case when ci.transaction_namespace = 'urn:fec:transaction' then 'federal'
                            when ci.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                            else 'other' end as state_or_federal,
                       -- ci.transaction_namespace,
                       amount
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
              ) x

            group by organization_entity, cycle, state_or_federal 
        )

    select  organization_entity,
            cycle,
            state_or_federal,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        org_contributions_by_cycle

    union all

    select  organization_entity,
            -1 as cycle,
            state_or_federal,
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
        group by organization_entity, state_or_federal
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_state_fed_entity_cycle_idx on aggregate_organization_to_state_fed (organization_entity, cycle)';
create index aggregate_organization_to_state_fed_idx on aggregate_organization_to_state_fed (organization_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_state_fed_party_cycle_idx on aggregate_organization_to_state_fed (transaction_namespace, cycle)';
create index aggregate_organization_to_state_fed_state_or_federal_cycle_idx on aggregate_organization_to_state_fed (state_or_federal,cycle);

-- Contributions to state and federal races from organizations and parent organizations
-- (to replace agg_namespace_from_org, total departure, based on aggregate_organizations_by...)
-- difference: doesn't cut off at top 10, doesn't include industries or individuals, includes pacs and cands
-- test: join with agg_party_from_org using (organization_entity, cycle, transaction_namespace), check
--
-- SELECT 723503
-- Time: 1715568.813 ms
-- CREATE INDEX
-- Time: 1641.378 ms
-- CREATE INDEX
-- Time: 12908.539 ms


select date_trunc('second', now()) || ' -- drop table if exists aggregate_organization_to_seat';
drop table if exists aggregate_organization_to_seat cascade;

select date_trunc('second', now()) || ' -- create table aggregate_organization_to_seat';
create table aggregate_organization_to_seat as
    with org_contributions_by_cycle as
        (select organization_entity,
                cycle,
                seat,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by organization_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by organization_entity, cycle order by sum(amount) desc) as rank_by_amount
            from

               ( select ca.entity_id as organization_entity,
                       cycle,
                       co.seat,
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
                group by ca.entity_id, cycle, seat

            union all

                select oa.entity_id as organization_entity,
                       cycle,
                       ci.seat,
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
                group by oa.entity_id, cycle, seat) x

            group by organization_entity, cycle, seat
        )

    select  organization_entity,
            cycle,
            seat,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        org_contributions_by_cycle

    union all

    select  organization_entity,
            -1 as cycle,
            seat,
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

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_seat_entity_cycle_idx on aggregate_organization_to_seat (organization_entity, cycle)';
create index aggregate_organization_to_seat_idx on aggregate_organization_to_seat (organization_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_seat_seat_cycle_idx on aggregate_organization_to_seat (seat, cycle)';
create index aggregate_organization_to_seat_seat_cycle_idx on aggregate_organization_to_seat (seat, cycle);

-- CONTRIBUTIONS FROM ORGANIZATIONS TO RECIPIENT TYPES
-- SELECT 363313
-- Time: 1955652.728 ms
-- CREATE INDEX
-- Time: 939.096 ms
-- CREATE INDEX
-- Time: 2062.522 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_organization_to_recipient_type';
drop table if exists aggregate_organization_to_recipient_type cascade;

select date_trunc('second', now()) || ' -- create table aggregate_organization_to_recipient_type';
create table aggregate_organization_to_recipient_type as
    with org_contributions_by_cycle as
        (select organization_entity,
                cycle,
                recipient_type,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by organization_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by organization_entity, cycle order by sum(amount) desc) as rank_by_amount
            from

               ( select ca.entity_id as organization_entity,
                       cycle,
                       co.recipient_type,
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
                group by ca.entity_id, cycle, recipient_type

            union all

                select oa.entity_id as organization_entity,
                       cycle,
                       ci.recipient_type,
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
                group by oa.entity_id, cycle, recipient_type) x

            group by organization_entity, cycle, recipient_type
        )

    select  organization_entity,
            cycle,
            recipient_type,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        org_contributions_by_cycle

    union all

    select  organization_entity,
            -1 as cycle,
            recipient_type,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        (select organization_entity,
                recipient_type,
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by organization_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by organization_entity order by sum(amount) desc) as rank_by_amount
        from
            org_contributions_by_cycle
        group by organization_entity, recipient_type
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_recipient_type_entity_cycle_idx on aggregate_organization_to_recipient_type (organization_entity, cycle)';
create index aggregate_organization_to_recipient_type_idx on aggregate_organization_to_recipient_type (organization_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_organization_to_recipient_type_recipient_type_cycle_idx on aggregate_organization_to_recipient_type (recipient_type, cycle)';
create index aggregate_organization_to_recipient_type_recipient_type_cycle_idx on aggregate_organization_to_recipient_type (recipient_type, cycle);



---- INDIVIDUALS

-- Contributions to state and federal races from individuals
-- to replace agg_namespace_from_indiv
-- difference: doesn't cut off at top 10, doesn't filter for recip party, contributor type or namespace explicity, includes pacs and cands
-- test: join with agg_namespace_from_indiv using (individual_entity, cycle, transaction_namespace), check
-- 
-- SELECT 130140
-- Time: 924001.302 ms
-- CREATE INDEX
-- Time: 304.081 ms
-- CREATE INDEX
-- Time: 1472.572 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_individual_to_state_fed';
drop table if exists aggregate_individual_to_state_fed cascade;

select date_trunc('second', now()) || ' -- create table aggregate_individual_to_state_fed';
create table aggregate_individual_to_state_fed as
    with contributions_by_cycle as
        (select entity_id as individual_entity,
                       cycle,
                       state_or_federal,
                       count(*) as count,
                       sum(amount) as amount,
                        rank() over (partition by entity_id, cycle order by count(*) desc) as rank_by_count,
                        rank() over (partition by entity_id, cycle order by sum(amount) desc) as rank_by_amount
                from
                    (
                    select ca.entity_id,
                       case when transaction_namespace = 'urn:fec:transaction' then 'federal'
                            when transaction_namespace = 'urn:nimsp:transaction' then 'state'
                            else 'other' end as state_or_federal,
                       -- ci.transaction_namespace,
                       cycle,
                       amount
                    from
                    (table contributions_individual
                     union table contributions_individual_to_organization ) ci
                        inner join
                    contributor_associations ca using (transaction_id)
                        left join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity re on re.id = ra.entity_id
                    ) sf
                group by entity_id, cycle, state_or_federal)

    select  individual_entity,
            cycle,
            state_or_federal,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  individual_entity,
            -1 as cycle,
            state_or_federal,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        (select individual_entity,
                state_or_federal,
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by individual_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by individual_entity order by sum(amount) desc) as rank_by_amount
        from
            contributions_by_cycle
        group by individual_entity, state_or_federal) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_individual_to_state_fed_entity_cycle_idx on aggregate_individual_to_state_fed (individual_entity, cycle)';
create index aggregate_individual_to_state_fed_idx on aggregate_individual_to_state_fed (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_individual_to_state_fed_party_cycle_idx on aggregate_individual_to_state_fed (state_or_federal, cycle)';
create index aggregate_individual_to_state_fed_state_fed_cycle_idx on aggregate_individual_to_state_fed (state_or_federal, cycle);

-- Contributions to state and federal races from individuals
-- to replace agg_party_from_indiv
-- difference: doesn't cut off at top 10, doesn't filter for recip party, contributor type or namespace explicity, includes pacs and cands
-- test: join with agg_party_from_indiv using (individual_entity, cycle, transaction_namespace), check
-- 
-- SELECT 163226
-- Time: 717640.708 ms
-- CREATE INDEX
-- Time: 366.431 ms
-- CREATE INDEX
-- Time: 857.155 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_individual_to_parties';
drop table if exists aggregate_individual_to_parties cascade;

select date_trunc('second', now()) || ' -- create table aggregate_individual_to_parties';
create table aggregate_individual_to_parties as
    with contributions_by_cycle as
        (select ca.entity_id as individual_entity,
                       cycle,
                       ci.recipient_party,
                       count(*) as count,
                       sum(ci.amount) as amount,
                        rank() over (partition by ca.entity_id, cycle order by count(*) desc) as rank_by_count,
                        rank() over (partition by ca.entity_id, cycle order by sum(ci.amount) desc) as rank_by_amount
                from
                    (table contributions_individual
                     union table contributions_individual_to_organization ) ci
                        inner join
                    contributor_associations ca using (transaction_id)
                    group by ca.entity_id, cycle, ci.recipient_party)

    select  individual_entity,
            cycle,
            recipient_party,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  individual_entity,
            -1 as cycle,
            recipient_party,
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
        group by individual_entity, recipient_party
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_individual_to_parties_entity_cycle_idx on aggregate_individual_to_parties (individual_entity, cycle)';
create index aggregate_individual_to_parties_idx on aggregate_individual_to_parties (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_recipient_parties_from_individual_party_cycle_idx on aggregate_individual_to_parties (recipient_party, cycle)';
create index aggregate_individual_to_parties_party_cycle_idx on aggregate_individual_to_parties (recipient_party, cycle);


 -- CONTRIBUTIONS FROM INDIVIDUALS BY GROUP/POLITICIAN
-- SELECT 145440
-- Time: 716827.005 ms
-- CREATE INDEX
-- Time: 318.868 ms
-- CREATE INDEX
-- Time: 769.794 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_individual_to_recipient_types';
drop table if exists aggregate_individual_to_recipient_types cascade;

select date_trunc('second', now()) || ' -- create table aggregate_individual_to_recipient_types';
create table aggregate_individual_to_recipient_types as
    with contributions_by_cycle as
        (select 
                ca.entity_id as individual_entity,
                cycle,
                ci.recipient_type,
                count(*) as count,
                sum(ci.amount) as amount,
                rank() over (partition by ca.entity_id, cycle order by count(*) desc) as rank_by_count,
                rank() over (partition by ca.entity_id, cycle order by sum(ci.amount) desc) as rank_by_amount
         from
                (table contributions_individual
                union table contributions_individual_to_organization ) ci
                        inner join
                contributor_associations ca using (transaction_id)
                group by ca.entity_id, cycle, ci.recipient_type)

    select  
            individual_entity,
            cycle,
            recipient_type,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  
            individual_entity,
            -1 as cycle,
            recipient_type,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        (select 
                individual_entity,
                recipient_type,
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by individual_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by individual_entity order by sum(amount) desc) as rank_by_amount
        from
            contributions_by_cycle
        group by individual_entity, recipient_type
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_individual_to_recipient_types_entity_cycle_idx on aggregate_individual_to_recipient_types (individual_entity, cycle)';
create index aggregate_individual_to_recipient_types_idx on aggregate_individual_to_recipient_types (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_individual_to_recipient_types_type_cycle_idx on aggregate_individual_to_recipient_types (recipient_type, cycle)';
create index aggregate_individual_to_recipient_types_party_cycle_idx on aggregate_individual_to_recipient_types (recipient_type, cycle);


-- Contributions to in state and out of state policitians from individuals
-- to replace agg_in_state_out_of_state_from_indiv
-- difference: doesn't cut off at top 10, doesn't filter for recip party, contributor type or namespace explicity, includes pacs and cands
-- test: join with agg_party_from_indiv using (individual_entity, cycle, transaction_namespace), check
-- debug: none
-- SELECT 112552
-- Time: 70458.033 ms
-- CREATE INDEX
-- Time: 253.094 ms
-- CREATE INDEX
-- Time: 1874.061 msi

select date_trunc('second', now()) || ' -- drop table if exists aggregate_individual_by_in_state_out_of_state';
drop table if exists aggregate_individual_by_in_state_out_of_state cascade;

select date_trunc('second', now()) || ' -- create table aggregate_individual_by_in_state_out_of_state';
create table aggregate_individual_by_in_state_out_of_state as
    with contributions_by_cycle as
        (select individual_entity,
                cycle,
                in_state_out_of_state,
                count(*) as count,
                sum(amount) as amount,
                rank() over (partition by individual_entity, cycle order by count(*) desc) as rank_by_count,
                rank() over (partition by individual_entity, cycle order by sum(amount) desc) as rank_by_amount
                from
                    (select ca.entity_id as individual_entity,
                                   ci.cycle,
                                case    when ci.contributor_state = ci.recipient_state then 'in-state'
                                        when ci.contributor_state = '' then ''
                                        else 'out-of-state' end as in_state_out_of_state,
                                   amount
                            from
                                contributions_individual ci
                                    inner join
                                contributor_associations ca using (transaction_id)
                                    inner join
                                recipient_associations ra using (transaction_id)
                                    inner join
                                matchbox_politicianmetadata mpm on mpm.entity_id = ra.entity_id and mpm.cycle = ci.cycle
                            where
                                mpm.seat != 'federal:president'
                    ) x
                group by individual_entity, cycle, in_state_out_of_state)

    select  individual_entity,
            cycle,
            in_state_out_of_state,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  individual_entity,
            -1 as cycle,
            in_state_out_of_state,
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
        group by individual_entity, in_state_out_of_state
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_individual_by_in_state_out_of_state_entity_cycle_idx on aggregate_individual_by_in_state_out_of_state (individual_entity, cycle)';
create index aggregate_individual_by_in_state_out_of_state_idx on aggregate_individual_by_in_state_out_of_state (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_individual_by_in_state_out_of_state_in_state_out_of_state_cycle_idx on aggregate_individual_by_in_state_out_of_state (in_state_out_of_state, cycle)';
create index aggregate_individual_by_in_state_out_of_state_in_state_out_of_state_cycle_idx on aggregate_individual_by_in_state_out_of_state (in_state_out_of_state, cycle);

-- Individuals: contributions to seat
-- 
-- SELECT 279285
-- Time: 719481.106 ms
-- CREATE INDEX
-- Time: 647.818 ms
-- CREATE INDEX
-- Time: 4539.257 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_individual_to_seat';
drop table if exists aggregate_individual_to_seat cascade;

select date_trunc('second', now()) || ' -- create table aggregate_individual_to_seat';
create table aggregate_individual_to_seat as
    with contributions_by_cycle as
        (select ca.entity_id as individual_entity,
                       cycle,
                       ci.seat,
                       count(*) as count,
                       sum(ci.amount) as amount,
                        rank() over (partition by ca.entity_id, cycle order by count(*) desc) as rank_by_count,
                        rank() over (partition by ca.entity_id, cycle order by sum(ci.amount) desc) as rank_by_amount
                from
                    (table contributions_individual
                     union table contributions_individual_to_organization ) ci
                        inner join
                    contributor_associations ca using (transaction_id)
                    group by ca.entity_id, cycle, ci.seat)

    select  individual_entity,
            cycle,
            seat,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  individual_entity,
            -1 as cycle,
            seat,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        (select individual_entity,
                    seat,
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by individual_entity order by sum(count) desc) as rank_by_count,
                rank() over(partition by individual_entity order by sum(amount) desc) as rank_by_amount
        from
            contributions_by_cycle
        group by individual_entity, seat
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_individual_to_seat_entity_cycle_idx on aggregate_individual_to_seat (individual_entity, cycle)';
create index aggregate_individual_to_seat_idx on aggregate_individual_to_seat (individual_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_individual_to_seat_seat_cycle_idx on aggregate_individual_to_seat (seat, cycle)';
create index aggregate_individual_to_seat_party_cycle_idx on aggregate_individual_to_seat (seat, cycle);


---- INDUSTRIES


-- Industries: Contributions to candidates
-- TODO: REDO
-- SELECT 11559299
-- Time: 2705139.576 ms
-- CREATE INDEX
-- Time: 30938.744 ms


select date_trunc('second', now()) || ' -- drop table if exists aggregate_industry_to_candidates';
drop table if exists aggregate_industry_to_candidates cascade;

select date_trunc('second', now()) || ' -- create table aggregate_industry_to_candidates';
create table aggregate_industry_to_candidates as
    with contributions_by_cycle as
        (select industry_entity,
                cycle,
                recipient_name,
                recipient_entity,
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
                       cycle,
                       coalesce(re.name, co.recipient_name) as recipient_name,
                       ra.entity_id as recipient_entity,
                       count(*) as count,
                       sum(co.amount) as amount
                from contributions_organization co -- this includes only recipient type 'P'
                        inner join
                    industry_associations ia using (transaction_id)
                        left join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity re on re.id = ra.entity_id
                group by ia.entity_id, cycle, ra.entity_id, coalesce(re.name, co.recipient_name)
                )  direct
            full outer join
                (
                select  ia.entity_id as industry_entity,
                        cycle,
                        coalesce(re.name, ci.recipient_name) as recipient_name,
                        ra.entity_id as recipient_entity,
                        count(*) as count,
                        sum(amount) as amount
                from
                    contributions_individual ci -- this includes only recipient type 'P'
                        inner join
                    industry_associations ia using (transaction_id)
                        left join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity re on re.id = ra.entity_id
                group by ia.entity_id, cycle, ra.entity_id, coalesce(re.name, ci.recipient_name)
                ) indivs
        using (industry_entity, cycle, recipient_entity, recipient_name)
    )

    select  
            industry_entity,
            cycle,
            recipient_name,
            recipient_entity,
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
            -1 as cycle,
            recipient_name,
            recipient_entity,
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
        group by industry_entity, recipient_entity, recipient_name
        ) all_cycle_rollup

;

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_candidates_idx on aggregate_industry_to_candidates (industry_entity, cycle)';
create index aggregate_industry_to_candidates_idx on aggregate_industry_to_candidates (industry_entity, cycle);

-- Contributions to committees from industries
-- TODO: REDO
-- SELECT 1101014
-- Time: 875607.622 ms
-- CREATE INDEX
-- Time: 2900.151 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_industry_to_pacs';
drop table if exists aggregate_industry_to_pacs cascade;

select date_trunc('second', now()) || ' -- create table aggregate_industry_to_pacs';
create table aggregate_industry_to_pacs as
    with contributions_by_cycle as
        (select industry_entity,
                cycle,
                recipient_name,
                recipient_entity,
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
                       cycle,
                       coalesce(re.name, c.recipient_name) as recipient_name,
                       ra.entity_id as recipient_entity,
                       count(*),
                       sum(c.amount) as amount
                from contributions_org_to_pac c
                        inner join
                    industry_associations ia using (transaction_id)
                        left join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity re on re.id = ra.entity_id
                group by ia.entity_id, cycle, ra.entity_id, coalesce(re.name, c.recipient_name)
                )  direct
            full outer join
                (
                select  ia.entity_id as industry_entity,
                        cycle,
                        coalesce(re.name, c.recipient_name) as recipient_name,
                        ra.entity_id as recipient_entity,
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
                group by ia.entity_id, cycle, ra.entity_id, coalesce(re.name, c.recipient_name)
                ) indivs
        using (industry_entity, cycle, recipient_entity, recipient_name)
    )

    select  industry_entity,
            cycle,
            recipient_name,
            recipient_entity,
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
            -1 as cycle,
            recipient_name,
            recipient_entity,
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
        group by industry_entity, recipient_entity, recipient_name
        ) all_cycle_rollup

;

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_pacs_idx on aggregate_industry_to_pacs (industry_entity, cycle)';
create index aggregate_industry_to_pacs_idx on aggregate_industry_to_pacs (industry_entity, cycle);

-- CONTRIBUTIONS FROM ORGS BY ASSOCIATED INDIV/PAC
-- SELECT 14786
-- Time: 92474.371 ms
-- CREATE INDEX
-- Time: 555.306 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_industry_by_indiv_pac';
drop table if exists aggregate_industry_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table aggregate_industry_by_indiv_pac';
create table aggregate_industry_by_indiv_pac as
    with contributions_by_cycle as
        (select
            industry_entity,
            cycle,
            sum(pacs_count) as pacs_count,
            sum(pacs_amount) as pacs_amount,
            sum(indivs_count) as indivs_count,
            sum(indivs_amount) as indivs_amount
            from
                (table aggregate_industry_to_candidates
                 union table aggregate_industry_to_pacs) as aggs
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

select date_trunc('second', now()) || ' -- create index aggregate_industry_by_indiv_pac_cycle_rank_idx on aggregate_industry_by_indiv_pac (cycle, organization_entity)';
create index aggregate_industry_by_indiv_pac_cycle_rank_by_amount_idx on aggregate_industry_by_indiv_pac (cycle, industry_entity);

-- Contributions to parties from industry
-- SELECT 38982
-- Time: 1hr43m21s
-- CREATE INDEX
-- Time: milliseconds
-- CREATE INDEX
-- Time: milliseconds

select date_trunc('second', now()) || ' -- drop table if exists aggregate_industry_to_parties';
drop table if exists aggregate_industry_to_parties cascade;

select date_trunc('second', now()) || ' -- create table aggregate_industry_to_parties';
create table aggregate_industry_to_parties as
    with contributions_by_cycle as
        (select industry_entity,
                cycle,
                recipient_party,
                sum(count) as count,
                sum(amount) as amount,
                rank() over (partition by industry_entity, cycle order by sum(count) desc) as rank_by_count,
                rank() over (partition by industry_entity, cycle order by sum(amount) desc) as rank_by_amount
            from

               ( select ia.entity_id as industry_entity,
                       cycle,
                       co.recipient_party,
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
                group by ia.entity_id, cycle, co.recipient_party

            union all

                select ia.entity_id as industry_entity,
                       cycle,
                       ci.recipient_party,
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
                group by ia.entity_id, cycle, ci.recipient_party) x

            group by industry_entity, cycle, recipient_party
        )

    select  industry_entity,
            cycle,
            recipient_party,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  industry_entity,
            -1 as cycle,
            recipient_party,
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

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_parties_entity_cycle_idx on aggregate_industry_to_parties (industry_entity, cycle)';
create index aggregate_industry_to_parties_idx on aggregate_industry_to_parties (industry_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_parties_party_cycle_idx on aggregate_industry_to_parties (recipient_party, cycle)';
create index aggregate_industry_to_parties_party_cycle_idx on aggregate_industry_to_parties (recipient_party, cycle);



-- Contributions to state and federal races from industries
-- SELECT 13523
-- Time: 6132337.616 ms
-- CREATE INDEX
-- Time: 45.683 ms
-- CREATE INDEX
-- Time: 138.150 ms
select date_trunc('second', now()) || ' -- drop table if exists aggregate_industry_to_state_fed';
drop table if exists aggregate_industry_to_state_fed cascade;

select date_trunc('second', now()) || ' -- create table aggregate_industry_to_state_fed';
create table aggregate_industry_to_state_fed as
    with contributions_by_cycle as
        (select industry_entity,
                cycle,
                state_or_federal,
                count(*) as count,
                sum(amount) as amount,
                rank() over (partition by industry_entity, cycle order by count(*) desc) as rank_by_count,
                rank() over (partition by industry_entity, cycle order by sum(amount) desc) as rank_by_amount
            from
            (
                select ia.entity_id as industry_entity,
                           cycle,
                           case when co.transaction_namespace = 'urn:fec:transaction' then 'federal'
                                when co.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                                else 'other' end as state_or_federal,
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

            union all

                select ia.entity_id as industry_entity,
                           cycle,
                           case when ci.transaction_namespace = 'urn:fec:transaction' then 'federal'
                                when ci.transaction_namespace = 'urn:nimsp:transaction' then 'state'
                                else 'other' end as state_or_federal,
                           ci.amount
                from
                    (table contributions_individual
                     union table contributions_individual_to_organization) ci
                        inner join
                    industry_associations ia using (transaction_id)
                        left join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity re on re.id = ra.entity_id
            ) x

            group by industry_entity, cycle, state_or_federal
        )

    select  industry_entity,
            cycle,
            state_or_federal,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  industry_entity,
            -1 as cycle,
            state_or_federal,
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
        group by industry_entity, state_or_federal
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_state_fed_entity_cycle_idx on aggregate_industry_to_state_fed (industry_entity, cycle)';
create index aggregate_industry_to_state_fed_idx on aggregate_industry_to_state_fed (industry_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_state_fed_party_cycle_idx on aggregate_industry_to_state_fed (recipient_party, cycle)';
create index aggregate_industry_to_state_fed_state_fed_cycle_idx on aggregate_industry_to_state_fed (state_or_federal, cycle);

-- Contributions to recipient types from industries
-- SELECT 14583   
-- Time: 6132288.223 ms
-- CREATE INDEX   
-- Time: 36.544 ms
-- CREATE INDEX
-- Time: 65.805 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_industry_to_recipient_type';
drop table if exists aggregate_industry_to_recipient_type cascade;

select date_trunc('second', now()) || ' -- create table aggregate_industry_to_recipient_type';
create table aggregate_industry_to_recipient_type as
    with contributions_by_cycle as
        (select industry_entity,
                cycle,
                recipient_type,
                count(*) as count,
                sum(amount) as amount,
                rank() over (partition by industry_entity, cycle order by count(*) desc) as rank_by_count,
                rank() over (partition by industry_entity, cycle order by sum(amount) desc) as rank_by_amount
            from
            (
                select ia.entity_id as industry_entity,
                           cycle,
                           recipient_type,
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

            union all

                select ia.entity_id as industry_entity,
                           cycle,
                           recipient_type,
                           ci.amount
                from
                    (table contributions_individual
                     union table contributions_individual_to_organization) ci
                        inner join
                    industry_associations ia using (transaction_id)
                        left join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity re on re.id = ra.entity_id
            ) x

            group by industry_entity, cycle, recipient_type
        )

    select  industry_entity,
            cycle,
            recipient_type,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  industry_entity,
            -1 as cycle,
            recipient_type,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        (select industry_entity,
                recipient_type,
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by recipient_type order by sum(count) desc) as rank_by_count,
                rank() over(partition by recipient_type order by sum(amount) desc) as rank_by_amount
        from
            contributions_by_cycle
        group by industry_entity, recipient_type
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_recipient_type_entity_cycle_idx on aggregate_industry_to_recipient_type (industry_entity, cycle)';
create index aggregate_industry_to_recipient_type_idx on aggregate_industry_to_recipient_type (industry_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_industry_to_recipient_type_party_cycle_idx on aggregate_industry_to_recipient_type (recipient_party, cycle)';
create index aggregate_industry_to_recipient_type_recipient_type_cycle_idx on aggregate_industry_to_recipient_type (recipient_type, cycle);

-- Politicians: Contributions from Organizations
-- SELECT 7141870
-- Time: 783032.244 ms
-- CREATE INDEX
-- Time: 22240.377 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_politician_from_organizations';
drop table if exists aggregate_politician_from_organizations cascade;

select date_trunc('second', now()) || ' -- create table aggregate_politician_from_organizations';
create table aggregate_politician_from_organizations as
    with contributions_by_cycle as
        (select recipient_entity as politician_entity,
                cycle,
                organization_entity,
                organization_name,
                coalesce(direct.count, 0) + coalesce(indivs.count, 0) as total_count,
                coalesce(direct.count, 0) as pacs_count,
                coalesce(indivs.count, 0) as indivs_count,
                coalesce(direct.amount, 0) + coalesce(indivs.amount, 0) as total_amount,
                coalesce(direct.amount, 0) as pacs_amount,
                coalesce(indivs.amount, 0) as indivs_amount,
                rank() over (partition by recipient_entity, cycle order by (coalesce(direct.amount, 0) + coalesce(indivs.amount, 0)) desc) as rank_by_amount,
                rank() over (partition by recipient_entity, cycle order by (coalesce(direct.count, 0) + coalesce(indivs.count, 0)) desc) as rank_by_count 
            from
                (
                select 
                       ra.entity_id as recipient_entity,
                       cycle,
                       ca.entity_id as organization_entity,
                       coalesce(ce.name, c.contributor_name) as organization_name,
                       count(*),
                       sum(c.amount) as amount
                from contributions_organization c
                        inner join
                    (table organization_associations
                     union table parent_organization_associations
                                                             ) ca using (transaction_id)
                        inner join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity ce on ce.id = ca.entity_id
                where coalesce(ce.name, c.contributor_name) != ''
                group by ra.entity_id, cycle, ca.entity_id, coalesce(ce.name, c.contributor_name)
                )  direct
            full outer join
                (
                select  
                       ra.entity_id as recipient_entity,
                       cycle,
                       oa.entity_id as organization_entity,
                       coalesce(ce.name, c.contributor_name) as organization_name,
                       count(*),
                       sum(c.amount) as amount
                from
                    contributions_individual c
                        inner join
                    (table organization_associations
                     union table parent_organization_associations
                                                            ) oa using (transaction_id)
                        inner join
                    recipient_associations ra using (transaction_id)
                        left join
                    matchbox_entity ce on ce.id = oa.entity_id
                group by ra.entity_id, cycle, oa.entity_id, coalesce(ce.name, c.contributor_name)
                ) indivs
        using (recipient_entity, cycle, organization_entity, organization_name)
    )

    select  
            politician_entity,
            cycle,
            organization_entity,
            organization_name,
            total_count,
            pacs_count,
            indivs_count,
            total_amount,
            pacs_amount,
            indivs_amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select
            politician_entity,
            -1 as cycle,
            organization_entity,
            organization_name,
            total_count,
            pacs_count,
            indivs_count,
            total_amount,
            pacs_amount,
            indivs_amount,
            rank_by_count,
            rank_by_amount
    from
        (select
                politician_entity,
                organization_entity,
                organization_name,
                sum(total_count) as total_count,
                sum(pacs_count) as pacs_count,
                sum(indivs_count) as indivs_count,
                sum(total_amount) as total_amount,
                sum(pacs_amount) as pacs_amount,
                sum(indivs_amount) as indivs_amount,
                rank() over (partition by organization_entity order by sum(total_amount) desc) as rank_by_amount,
                rank() over (partition by organization_entity order by sum(total_count) desc) as rank_by_count
        from
            contributions_by_cycle
        group by politician_entity, organization_entity, organization_name
        ) all_cycle_rollup

;

select date_trunc('second', now()) || ' -- create index aggregate_politician_from_organizations_idx on aggregate_politician_from_organizations (organization_entity, cycle)';
create index aggregate_politician_from_organizations_idx on aggregate_politician_from_organizations (organization_entity, cycle);

-- Politicians: Reciepts from individuals
-- SELECT 273982
-- Time: 1374039.623 ms
-- CREATE INDEX
-- Time: 710.866 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_politician_from_organizations';
drop table if exists aggregate_politician_from_individuals cascade;

select date_trunc('second', now()) || ' -- create table aggregate_politician_from_individuals';
create table aggregate_politician_from_individuals as
    with contributions_by_cycle as
        (       select
                   ra.entity_id as politician_entity,
                   cycle,
                   ca.entity_id as individual_entity,
                   ce.name as individual_name,
                   count(*) as count,
                   sum(ci.amount) as amount,
                    rank() over (partition by ra.entity_id, cycle order by count(*) desc) as rank_by_count,
                    rank() over (partition by ra.entity_id, cycle order by sum(ci.amount) desc) as rank_by_amount
                from
                    contributions_individual ci
                        inner join
                    recipient_associations ra using (transaction_id)
                        inner join
                    contributor_associations ca using (transaction_id)
                        inner join
                    matchbox_entity ce on ce.id = ca.entity_id and ce.type = 'individual'
                        left join
                    (table organization_associations
                     union table parent_organization_associations) oa using (transaction_id) 
                where oa.entity_id is null
                group by ra.entity_id, cycle, ca.entity_id, ce.name)

    select
        politician_entity,
        cycle,
        individual_entity,
        individual_name,
        count,
        amount,
        rank_by_count,
        rank_by_amount
    from
        contributions_by_cycle

    union all

    select
        politician_entity,
        -1 as cycle,
        individual_entity,
        individual_name,
        count,
        amount,
        rank_by_count,
        rank_by_amount
    from
        (select 
            politician_entity,
            individual_entity,
            individual_name,
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by politician_entity order by sum(count) desc) as rank_by_count,
            rank() over(partition by politician_entity order by sum(amount) desc) as rank_by_amount
        from
            contributions_by_cycle
        group by politician_entity, individual_entity, individual_name
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_politician_from_individuals_entity_cycle_idx on aggregate_politician_from_individuals (politician_entity, cycle)';
create index aggregate_politician_from_individuals_idx on aggregate_politician_from_individuals (politician_entity, cycle);

-- Politicians: RECIEPTS FROM INDIVIDUALS VS ORG-ASSOCIATED INDIVIDUALS VS ORG PACS
-- SELECT 371151
-- Time: 116488.162 ms
-- CREATE INDEX
-- Time: 1135.104 ms


select date_trunc('second', now()) || ' -- drop table if exists aggregate_politician_by_org_pac_indiv';
drop table if exists aggregate_politician_by_org_pac_indiv;

select date_trunc('second', now()) || ' -- create table aggregate_politician_by_org_pac_indiv';
create table aggregate_politician_by_org_pac_indiv as
    select
        politician_entity,
        cycle,
        org_pac_indiv,
        sum(count) as count,
        sum(amount) as amount
    from
        (
        select
            politician_entity,
            cycle,
            'org_pac' as org_pac_indiv,
            pacs_count as count,
            pacs_amount as amount
        from
                aggregate_politician_from_organizations apo

        union all
        
        select
            politician_entity,
            cycle,
            'org_indiv' as org_pac_indiv,
            indivs_count as count,
            indivs_amount as amount
        from
                aggregate_politician_from_organizations apo

        union all

        select
            politician_entity,
            cycle,
            'indiv' as org_pac_indiv,
            count as count,
            amount as amount
        from
            aggregate_politician_from_individuals api
        ) cbc
            inner join
        matchbox_entity me on me.id = cbc.politician_entity
    group by
        politician_entity,
        cycle,
        org_pac_indiv
;

select date_trunc('second', now()) || ' -- create index aggregate_politician_by_org_pac_indiv_cycle_org_entity_idx on aggregate_politician_by_org_pac_indiv (cycle, politician_entity)';
create index aggregate_politician_by_org_pac_indiv_cycle_org_entity_idx on aggregate_politician_by_org_pac_indiv (cycle, politician_entity);



-- Politicians: reciepts from individuals by in-state/out-of-state
-- SELECT 84842
-- Time: 66398.101 ms
-- CREATE INDEX
-- Time: 192.887 ms
-- CREATE INDEX
-- Time: 1282.469 ms

select date_trunc('second', now()) || ' -- drop table if exists aggregate_politician_from_individuals_by_in_state_out_of_state';
drop table if exists aggregate_politician_from_individuals_by_in_state_out_of_state cascade;

select date_trunc('second', now()) || ' -- create table aggregate_politician_from_individuals_by_in_state_out_of_state';
create table aggregate_politician_from_individuals_by_in_state_out_of_state as
    with contributions_by_cycle as
        (select
                politician_entity,
                cycle,
                in_state_out_of_state,
                count(*) as count,
                sum(amount) as amount,
                rank() over (partition by politician_entity, cycle, in_state_out_of_state order by count(*) desc) as rank_by_count,
                rank() over (partition by politician_entity, cycle, in_state_out_of_state order by sum(amount) desc) as rank_by_amount
                from
                    (select 
                        ra.entity_id as politician_entity,
                            case    when ci.contributor_state = ci.recipient_state then 'in-state'
                                    when ci.contributor_state = '' then ''
                                    else 'out-of-state' end as in_state_out_of_state,
                               ci.cycle,
                               amount
                        from
                            contributions_individual ci
                                inner join
                            contributor_associations ca using (transaction_id)
                                inner join
                            recipient_associations ra using (transaction_id)
                                inner join
                            matchbox_entity ce on ce.id = ca.entity_id
                                inner join
                            matchbox_politicianmetadata mpm on mpm.entity_id = ra.entity_id and ci.cycle = mpm.cycle
                        where
                            mpm.seat != 'federal:president'
                    ) x
                group by politician_entity, cycle, in_state_out_of_state)

    select  
            politician_entity,
            cycle,
            in_state_out_of_state,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        contributions_by_cycle

    union all

    select  
            politician_entity,
            -1 as cycle,
            in_state_out_of_state,
            count,
            amount,
            rank_by_count,
            rank_by_amount
    from
        (select 
                politician_entity,
                in_state_out_of_state,
                sum(count) as count,
                sum(amount) as amount,
                rank() over(partition by politician_entity, in_state_out_of_state order by sum(count) desc) as rank_by_count,
                rank() over(partition by politician_entity, in_state_out_of_state order by sum(amount) desc) as rank_by_amount
        from
            contributions_by_cycle
        group by politician_entity, in_state_out_of_state
        ) all_cycle_rollup
;

select date_trunc('second', now()) || ' -- create index aggregate_politician_from_individuals_by_in_out_entity_cycle_idx on aggregate_politician_from_individuals_by_in_state_out_of_state (politician_entity, cycle)';
create index aggregate_politician_from_individuals_by_in_out_of_state_idx on aggregate_politician_from_individuals_by_in_state_out_of_state (politician_entity, cycle);

select date_trunc('second', now()) || ' -- create index aggregate_politician_from_individuals_by_in_out_inout_cycle_idx on aggregate_politician_from_individuals_by_in_state_out_of_state (in_state_out_of_state, cycle)';
create index aggregate_politician_from_individuals_by_in_out_inout_cycle_idx on aggregate_politician_from_individuals_by_in_state_out_of_state (in_state_out_of_state, cycle);



-- Politicians: reciepts from industries
-- SELECT 11556994
-- Time: 1596241.786 ms
-- CREATE INDEX
-- Time: 31148.489 ms`

select date_trunc('second', now()) || ' -- drop table if exists aggregate_politician_from_industries';
drop table if exists aggregate_politician_from_industries cascade;

select date_trunc('second', now()) || ' -- create table aggregate_politician_from_industries';
create table aggregate_politician_from_industries as
    with contributions_by_cycle as
        (select
                politician_entity,
                cycle,
                industry_name,
                industry_entity,
                coalesce(direct.count, 0) + coalesce(indivs.count, 0) as total_count,
                coalesce(direct.count, 0) as pacs_count,
                coalesce(indivs.count, 0) as indivs_count,
                coalesce(direct.amount, 0) + coalesce(indivs.amount, 0) as total_amount,
                coalesce(direct.amount, 0) as pacs_amount,
                coalesce(indivs.amount, 0) as indivs_amount,
                rank() over (partition by politician_entity, cycle order by (coalesce(direct.amount, 0) + coalesce(indivs.amount, 0)) desc) as rank
            from
                (
                select
                       ra.entity_id as politician_entity,
                       cycle,
                       ie.name as industry_name,
                       ia.entity_id as industry_entity,
                       count(*),
                       sum(co.amount) as amount
                from contributions_organization co -- this includes only recipient type 'P'
                        inner join
                    recipient_associations ra using (transaction_id)
                        inner join
                    industry_associations ia using (transaction_id)
                        inner join
                    matchbox_entity ie on ie.id = ia.entity_id
                group by ra.entity_id, cycle, ia.entity_id, ie.name
                )  direct
            full outer join
                (
                select
                       ra.entity_id as politician_entity,
                       ie.name as industry_name,
                       ia.entity_id as industry_entity,
                       cycle,
                       count(*),
                       sum(ci.amount) as amount
                from
                    contributions_individual ci -- this includes only recipient type 'P'
                        inner join
                    recipient_associations ra using (transaction_id)
                        inner join
                    industry_associations ia using (transaction_id)
                        inner join
                    matchbox_entity ie on ie.id = ia.entity_id
                group by ra.entity_id, cycle, ia.entity_id, ie.name
                ) indivs
        using (politician_entity, cycle, industry_entity, industry_name)
    )
    select
            politician_entity,
            cycle,
            industry_name,
            industry_entity,
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
            politician_entity,
            -1 as cycle,
            industry_name,
            industry_entity,
            total_count,
            pacs_count,
            indivs_count,
            total_amount,
            pacs_amount,
            indivs_amount,
            rank
    from
        (select
                politician_entity,
                industry_name,
                industry_entity,
                sum(total_count) as total_count,
                sum(pacs_count) as pacs_count,
                sum(indivs_count) as indivs_count,
                sum(total_amount) as total_amount,
                sum(pacs_amount) as pacs_amount,
                sum(indivs_amount) as indivs_amount,
                rank() over (partition by politician_entity order by sum(total_amount) desc) as rank
        from
            contributions_by_cycle
        group by politician_entity, industry_entity, industry_name
        ) all_cycle_rollup

;

select date_trunc('second', now()) || ' -- create index aggregate_politician_from_industries_idx on aggregate_politician_from_industries (politician_entity, cycle)';
create index aggregate_politician_from_industries_idx on aggregate_politician_from_industries (politician_entity, cycle);
