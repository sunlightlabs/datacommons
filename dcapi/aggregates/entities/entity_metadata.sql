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
        select distinct on (oa.entity_id)
            oa.entity_id,
            max(p.entity_id::text)::uuid as parent_entity_id,
            ia.entity_id as industry_entity_id
        from
            organization_associations oa
            left join parent_organization_associations p on oa.transaction_id = p.transaction_id and oa.entity_id != p.entity_id
            left join industry_associations ia on oa.transaction_id = ia.transaction_id
            left join matchbox_entityattribute ea on ea.entity_id = ia.entity_id
        where
            ea.namespace is null or ea.namespace in ('urn:crp:industry', 'urn:nimsp:industry')
        group by
            oa.entity_id, ia.entity_id
        order by
            oa.entity_id, count(distinct ia.transaction_id) desc
    ) contributing_orgs using (entity_id)
    group by entity_id;

delete from matchbox_organizationmetadata;

insert into matchbox_organizationmetadata (entity_id, lobbying_firm, parent_entity_id, industry_entity_id)
    select entity_id, lobbying_firm, parent_entity_id, industry_entity_id from tmp_matchbox_organizationmetadata;
commit;


begin;
analyze matchbox_organizationmetadata;
commit;


-- Politician Metadata

begin;
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

delete from  matchbox_politicianmetadata;

insert into matchbox_politicianmetadata (entity_id, cycle, state, state_held, district, district_held, party, seat, seat_held, seat_status, seat_result)
    select entity_id, cycle, state, state_held, district, district_held, party, seat, seat_held, seat_status, seat_result from tmp_matchbox_politicianmetadata;

commit;
begin;
analyze matchbox_politicianmetadata;
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

begin;
analyze matchbox_indivorgaffiliations;
commit;


-- Revolving Door Associations

begin;
create temp table tmp_matchbox_revolvingdoor as select * from matchbox_revolvingdoor limit 0;

insert into tmp_matchbox_revolvingdoor (politician_entity_id, lobbyist_entity_id)
    select distinct
        eap.entity_id as politician_entity_id,
        eal.entity_id as lobbyist_entity_id
    from
        lobbying_lobbyist l
        inner join matchbox_entityattribute eap
            on eap.value = l.candidate_ext_id
        inner join matchbox_entityattribute eal
            on eal.value = l.lobbyist_ext_id
    where
        eap.namespace = 'urn:crp:recipient' and eal.namespace = 'urn:crp:individual'
;

delete from matchbox_revolvingdoor;

insert into matchbox_revolvingdoor (politician_entity_id, lobbyist_entity_id)
    select politician_entity_id, lobbyist_entity_id from tmp_matchbox_revolvingdoor;
commit;

begin;
analyze matchbox_revolvingdoor;
commit;
