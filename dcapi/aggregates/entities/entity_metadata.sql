-- This data might some day be editable through a tool like Matchbox. For now just recompute it from the data.
-- Consider this a temporary hack until we have a more principled way of dealing with metadata.



-- Organization Metadata

delete from matchbox_organizationmetadata;

insert into matchbox_organizationmetadata (entity_id, lobbying_firm)
    select entity_id, bool_or(registrant_is_firm) as lobbying_firm
    from lobbying_report
    inner join assoc_lobbying_registrant using (transaction_id)
    group by entity_id;



-- Politician Metadata

delete from matchbox_politicianmetadata;
    
insert into matchbox_politicianmetadata (entity_id, state, party, seat)
    select distinct on (entity_id) entity_id, recipient_state, recipient_party, seat
    from contribution_contribution c
    inner join recipient_associations ra using (transaction_id)
    inner join matchbox_entity e on e.id = ra.entity_id
    where
        e.type = 'politician'
    order by entity_id, cycle desc;

        
