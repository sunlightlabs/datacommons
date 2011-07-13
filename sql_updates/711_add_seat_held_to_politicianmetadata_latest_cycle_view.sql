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

