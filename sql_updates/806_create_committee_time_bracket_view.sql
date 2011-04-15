create view politician_committee_timeline as
    select
        entity_id,
        name as committee_name,
        parent_name as parent_committee_name,
        is_chair,
        is_ranking,
        min(cycle) as from_year,
        max(cycle) as to_year
    from politician_committee
    group by entity_id, name, parent_name, is_chair, is_ranking
;
