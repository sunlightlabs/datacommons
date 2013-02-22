insert into matchbox_entityattribute (entity_id, namespace, value)
    select match_id, 'urn:pogo:contractor', contractor_ext_id
    from matching_pogo_matches_20111108_1123 m
    inner join pogo_contractor c on m.subject_id = c.id
    where confidence > 2
        and contractor_ext_id::integer not in (
            select value::integer from matchbox_entityattribute where namespace = 'urn:pogo:contractor'
        );
