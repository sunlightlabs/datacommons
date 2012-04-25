drop view organization_metadata_latest_cycle_view;
create or replace view organization_metadata_latest_cycle_view as
    select distinct on (entity_id)
        entity_id,
        cycle,
        lobbying_firm,
        parent_entity_id,
        industry_entity_id,
        subindustry_entity_id,
        is_superpac
    from matchbox_organizationmetadata
    where cycle <= 2012
    order by entity_id, cycle desc
;

create or replace view politician_metadata_latest_cycle_view as
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

