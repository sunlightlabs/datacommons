-- fill in the transaction count column

update matchbox_entity set transaction_count = (
    select count(*) from contribution_contribution 
    where contributor_entity = matchbox_entity.id
        or organization_entity = matchbox_entity.id
        or parent_organization_entity = matchbox_entity.id
        or committee_entity = matchbox_entity.id
        or recipient_entity = matchbox_entity.id
);


-- fill in the transaction amount total column

update matchbox_entity set transaction_amount = (
    select sum(amount) from contribution_contribution
    where contributor_entity = matchbox_entity.id
        or organization_entity = matchbox_entity.id
        or parent_organization_entity = matchbox_entity.id
        or committee_entity = matchbox_entity.id
        or recipient_entity = matchbox_entity.id
);


-- fill in the entity alias table

insert into matchbox_entityalias (entity_id, alias)
    (select contributor_entity, contributor_name
    from contribution_contribution
    where contributor_entity != ''
        and contributor_name != ''
    group by contributor_entity, contributor_name)
union
    (select organization_entity, organization_name
    from contribution_contribution
    where organization_entity != ''
        and organization_name != ''
    group by organization_entity, organization_name)
union
    (select organization_entity, contributor_employer
    from contribution_contribution
    where organization_entity != ''
        and contributor_employer != ''
    group by organization_entity, contributor_employer)
union
    (select parent_organization_entity, parent_organization_name
    from contribution_contribution
    where parent_organization_entity != ''
        and parent_organization_name != ''
    group by parent_organization_entity, parent_organization_name)
union
    (select committee_entity, committee_name
    from contribution_contribution
    where committee_entity != ''
        and committee_name != ''
    group by committee_entity, committee_name)
union
    (select recipient_entity, recipient_name
    from contribution_contribution
    where recipient_entity != ''
        and recipient_name != ''
    group by recipient_entity, recipient_name);


-- fill in the entity attributes table

-- todo: modify alias query for attributes