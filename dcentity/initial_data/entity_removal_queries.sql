-- Remove 'unique' individual entities with no matching ID
-- These are individuals that CRP has marked with a unique ID starting with 'U'
-- If the ID is no longer in the dataset then the entity will never be matched,
-- so may as well remove it.

create temporary table tmp_orphan_indivs as
    select e.id
    from matchbox_entity e
    inner join matchbox_entityattribute a on e.id = a.entity_id
    where
        e.type = 'individual'
        and substring(a.value for 1) = 'U'
        and not exists (
            select * 
            from contribution_contribution
            where contributor_ext_id = a.value)
        and not exists (
            select *
            from lobbying_lobbyist
            where lobbyist_ext_id = a.value
        );

delete from matchbox_entityattribute
where entity_id in (select * from tmp_orphan_indivs);


delete from matchbox_entityalias
where entity_id in (select * from tmp_orphan_indivs);


delete from matchbox_entity
where id in (select * from tmp_orphan_indivs);