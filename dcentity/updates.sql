
-- orphan individuals (to delete)

select e.id, e.name, a.value
from matchbox_entity e
inner join matchbox_entityattribute a
    on e.id = a.entity_id
where
    e.type = 'individual'
    and a.namespace = 'urn:crp:individual'
    and not exists (
        select * 
        from contribution_contribution c
        where c.contributor_ext_id = a.value)
    and not exists (
        select *
        from lobbying_lobbyist
        where lobbyist_ext_id = a.value
    );
    
-- orphan politicians (to delete)

select e.id, e.name, a.value
from matchbox_entity e
inner join matchbox_entityattribute a
    on e.id = a.entity_id
where
    e.type = 'politician'
    and not exists (
        select * 
        from contribution_contribution c
        where c.recipient_ext_id = a.value);

    
select a.entity_id, a.value
from matchbox_entityattribute a
where
    a.namespace = 'urn:crp:individual'
    and not exists (
        select * 
        from contribution_contribution c
        where c.contributor_ext_id = a.value)
    and not exists (
        select *
        from lobbying_lobbyist
        where lobbyist_ext_id = a.value
    );


-- new individuals (to add)

    select contributor_name, contributor_ext_id
    from contribution_contribution c
    where
        c.transaction_namespace = 'urn:fec:transaction'
        and substring(c.contributor_ext_id for 1) = 'U'
        and not exists (
            select * from matchbox_entityattribute where value = c.contributor_ext_id
        )
union
    select lobbyist_name, lobbyist_ext_id
    from lobbying_lobbyist
    where
        not exists (
            select * from matchbox_entityattribute where value = lobbyist_ext_id        
        );


-- new lobbying orgs (to add)

select l.registrant_name
from lobbying_lobbying l
where
    l.use = 't'
    and not exists (
        select * 
        from matchbox_entity e
        inner join matchbox_entityalias a
            on e.id = a.entity_id
        where
            e.type = 'organization'
            and lower(l.registrant_name) = lower(a.alias)
    )
group by registrant_name;



-- new politicians (to add)

select recipient_name, recipient_ext_id
from contribution_contribution c
where
    c.recipient_type = 'P'
    and not exists (
        select * from matchbox_entityattribute where value = c.recipient_ext_id
    );
