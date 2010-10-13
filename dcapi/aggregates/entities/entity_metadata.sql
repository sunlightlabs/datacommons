-- This data might some day be editable through a tool like Matchbox. For now just recompute it from the data.
-- Consider this a temporary hack until we have a more principled way of dealing with metadata.

-- Organization Metadata

begin;
create temp table tmp_matchbox_organizationmetadata as select * from matchbox_organizationmetadata limit 0;

insert into tmp_matchbox_organizationmetadata (entity_id, lobbying_firm, parent_entity_id, industry_entity_id)
    select
        entity_id,
        bool_or(coalesce(lobbying_firm, 'f')) as lobbying_firm,
        max(parent_entity_id) as parent_entity_id,
        max(industry_entity_id) as industry_entity_id
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
            max(p.entity_id) as parent_entity_id,
            max(ia.entity_id) as industry_entity_id
        from
            organization_associations oa
            left join parent_organization_associations p using (transaction_id)
            left join industry_associations ia using (transaction_id)
        group by
            oa.entity_id
        having
            max(p.entity_id) is null or oa.entity_id != max(p.entity_id)
    ) contributing_orgs using (entity_id)
    group by entity_id;

delete from matchbox_organizationmetadata;

insert into matchbox_organizationmetadata (entity_id, lobbying_firm, parent_entity_id, industry_entity_id)
    select entity_id, lobbying_firm, parent_entity_id, industry_entity_id from tmp_matchbox_organizationmetadata;
commit;


-- Politician Metadata

begin;
create temp table tmp_matchbox_politicianmetadata as select * from matchbox_politicianmetadata limit 0;

insert into tmp_matchbox_politicianmetadata (entity_id, state, party, seat)
    select distinct on (entity_id) entity_id, recipient_state, recipient_party, seat
    from contribution_contribution c
    inner join recipient_associations ra using (transaction_id)
    inner join matchbox_entity e on e.id = ra.entity_id
    where
        e.type = 'politician'
    order by entity_id, cycle desc;

delete from matchbox_politicianmetadata;

insert into matchbox_politicianmetadata (entity_id, state, party, seat)
    select entity_id, state, party, seat from tmp_matchbox_politicianmetadata;
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



