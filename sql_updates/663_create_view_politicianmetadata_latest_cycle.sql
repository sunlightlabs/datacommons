create view politician_metadata_latest_cycle_view as
    select distinct on (entity_id)
        entity_id,
        cycle,
        state,
        party,
        seat,
        seat_status,
        seat_result
    from matchbox_politicianmetadata
    order by entity_id, cycle desc
;

