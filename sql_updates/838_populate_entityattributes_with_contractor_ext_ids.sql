insert into matchbox_entityattribute (entity_id, namespace, value)
    select match_id, 'urn:pogo:contractor', contractor_ext_id
    from matching_pogo_matches_20110523_1051 m
    inner join pogo_contractor c on m.subject_id = c.id
    where confidence > 2;
