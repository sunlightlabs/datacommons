insert into matchbox_industrymetadata (entity_id, should_show_entity)
    select
        id as entity_id,
        'f' as should_show_entity
    from
        matchbox_entity
    where
        name in (
            'OTHER',
            'RETIRED',
            'HOMEMAKERS/NON-INCOME EARNERS',
            'NO EMPLOYER LISTED OR FOUND',
            'GENERIC OCCUPATION/CATEGORY UNKNOWN',
            'EMPLOYER LISTED/CATEGORY UNKNOWN',
            'NON-CONTRIBUTION'
        )
        or name ilike 'misc %'
;

