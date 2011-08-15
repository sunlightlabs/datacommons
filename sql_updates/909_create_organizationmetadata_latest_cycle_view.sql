create or replace view organization_metadata_latest_cycle_view as
    select distinct on (entity_id)
        entity_id,
        cycle,
        lobbying_firm,
        parent_entity_id,
        industry_entity_id
    from matchbox_organizationmetadata
    order by entity_id, cycle desc
;
