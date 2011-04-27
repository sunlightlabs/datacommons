create view politician_committee_timeline as
    select
        entity_id,
        min(name) as committee_name,
        parent_code as parent_committee_code,
        is_chair,
        is_ranking,
        min(cycle) as from_year,
        max(cycle) as to_year
    from politician_committee
    group by entity_id, code, parent_code, is_chair, is_ranking
;
