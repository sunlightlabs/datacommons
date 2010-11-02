
-- orphan individuals (to delete)

create table tmp_individuals_to_delete as
    select e.id, e.name, a.value
    from matchbox_entity e
    inner join matchbox_entityattribute a on e.id = a.entity_id
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
        )
;

-- orphan politicians (to delete)

create table tmp_politicians_to_delete as
    select e.id, e.name, a.value
    from matchbox_entity e
    inner join matchbox_entityattribute a on e.id = a.entity_id
    where
        e.type = 'politician'
        and not exists (
            select *
            from contribution_contribution c
            where c.recipient_ext_id = a.value
        )
;


-- new individuals (to add)

create table tmp_individuals as
    select min(name), id from (
        select min(lobbyist_name) as name, lobbyist_ext_id as id
        from lobbying_lobbyist
        where
            lobbyist_name != ''
            and not exists (select * from matchbox_entityattribute where value = lobbyist_ext_id)
        group by lobbyist_ext_id

        union

        select min(contributor_name) as name, contributor_ext_id as id
        from contribution_contribution
        where
            contributor_name != ''
            and contributor_ext_id like 'U%'
            and not exists (select * from lobbying_lobbyist where lobbyist_ext_id = contributor_ext_id)
            and not exists (select * from matchbox_entityattribute where value = contributor_ext_id)
        group by contributor_ext_id
    )x
    group by id
;


-- new lobbying orgs (to add)

create table tmp_lobbying_orgs as
    select 0 as crp_id, 0 as nimsp_id, max(l.registrant_name) as name
    from lobbying_lobbying l
    where
        l.use = 't'
        and registrant_name != ''
        and not exists (
            select *
            from matchbox_entity e
            inner join matchbox_entityalias a on e.id = a.entity_id
            where
                e.type = 'organization'
                and lower(l.registrant_name) = lower(a.alias)
        )
    group by lower(registrant_name)
;



-- new politicians (to add)

create table tmp_politicians as
    select min(recipient_name) as name, transaction_namespace as namespace, recipient_ext_id as id
    from contribution_contribution
    where
        recipient_type = 'P'
        and recipient_name != ''
        and recipient_ext_id != ''
        and not exists (select * from matchbox_entityattribute where value = recipient_ext_id)
    group by transaction_namespace, recipient_ext_id
;
