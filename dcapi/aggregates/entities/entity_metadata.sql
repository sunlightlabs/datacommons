-- This data might some day be editable through a tool like Matchbox. For now just recompute it from the data.
-- Consider this a temporary hack until we have a more principled way of dealing with metadata.

-- Organization Metadata

begin;
create temp table tmp_matchbox_organizationmetadata as select * from matchbox_organizationmetadata limit 0;

insert into tmp_matchbox_organizationmetadata (entity_id, lobbying_firm, parent_entity_id, industry_entity_id)
    select
        entity_id,
        bool_or(coalesce(lobbying_firm, 'f')) as lobbying_firm,
        max(parent_entity_id::text)::uuid as parent_entity_id,
        max(industry_entity_id::text)::uuid as industry_entity_id
    from (
        select
            entity_id,
            bool_or(registrant_is_firm) as lobbying_firm
        from
            lobbying_report
            inner join assoc_lobbying_registrant using (transaction_id)
        group by
            entity_id
    ) lobbying_orgs
    full outer join (
        select
            oa.entity_id,
            max(p.entity_id::text) as parent_entity_id,
            max(ia.entity_id::text) as industry_entity_id
        from
            organization_associations oa
            left join parent_organization_associations p using (transaction_id)
            left join industry_associations ia using (transaction_id)
        group by
            oa.entity_id
        having
            max(p.entity_id::text) is null or oa.entity_id::text != max(p.entity_id::text)
    ) contributing_orgs using (entity_id)
    group by entity_id;

delete from matchbox_organizationmetadata;

insert into matchbox_organizationmetadata (entity_id, lobbying_firm, parent_entity_id, industry_entity_id)
    select entity_id, lobbying_firm, parent_entity_id, industry_entity_id from tmp_matchbox_organizationmetadata;
commit;


-- Politician Metadata

begin;
drop view if exists politician_metadata_latest_cycle_view;
create temp table tmp_matchbox_politicianmetadata as select * from matchbox_politicianmetadata limit 0;

insert into tmp_matchbox_politicianmetadata (entity_id, cycle, state, state_held, district, district_held, party, seat, seat_held, seat_status, seat_result)
    select
        entity_id,
        cycle,
        max(recipient_state) as state,
        max(recipient_state_held) as state_held,
        max(district) as district,
        max(district_held) as district_held,
        max(recipient_party) as party,
        max(seat) as seat,
        max(seat_held) as seat_held,
        max(seat_status) as seat_status,
        max(seat_result) as seat_result
    from contribution_contribution c
    inner join recipient_associations ra using (transaction_id)
    inner join matchbox_entity e on e.id = ra.entity_id
    where
        e.type = 'politician'
    group by entity_id, cycle
;

drop table matchbox_politicianmetadata;

alter table tmp_matchbox_politicianmetadata rename to matchbox_politicianmetadata;

create view politician_metadata_latest_cycle_view as
    select distinct on (entity_id)
        entity_id,
        cycle,
        state,
        state_held,
        district,
        district_held,
        party,
        seat,
        seat_held,
        seat_status,
        seat_result
    from matchbox_politicianmetadata
    order by entity_id, cycle desc
;

commit;


-- Indiv/Org Affiliations

begin;
create temp table tmp_matchbox_indivorgaffiliations as select * from matchbox_indivorgaffiliations limit 0;

insert into tmp_matchbox_indivorgaffiliations (individual_entity_id, organization_entity_id)
    select distinct
        ca.entity_id as individual_entity_id, oa.entity_id as organization_entity_id
    from
        contributor_associations ca
        inner join organization_associations oa using (transaction_id)
        inner join matchbox_entity me on me.id = ca.entity_id
    where me.type = 'individual';

delete from matchbox_indivorgaffiliations;

insert into matchbox_indivorgaffiliations (individual_entity_id, organization_entity_id)
    select individual_entity_id, organization_entity_id from tmp_matchbox_indivorgaffiliations;
commit;


