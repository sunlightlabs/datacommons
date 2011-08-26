drop view if exists tmp_org_lobbyist_contribution_overlap;
drop view if exists tmp_org_contributions;
drop view if exists tmp_org_lobbyist_contributions;


create view tmp_org_contributions as
select oa.entity_id as org_entity, ra.entity_id as recipient_entity, sum(amount) as amount
from contributions_all_relevant c
inner join (table contributor_associations union table organization_associations union table parent_organization_associations) oa 
    on oa.transaction_id = c.transaction_id
inner join recipient_associations ra on ra.transaction_id = c.transaction_id
where
    cycle = 2010
group by oa.entity_id, ra.entity_id;


create view tmp_org_lobbyist_contributions as
select client_entity, lobbyist_entity, recipient_entity, sum(amount) as amount
from (
    select alc.entity_id as client_entity, ca.entity_id as lobbyist_entity, ra.entity_id as recipient_entity, c.transaction_id, c.amount
    from contributions_all_relevant c
    inner join contributor_associations ca on ca.transaction_id = c.transaction_id 
    inner join recipient_associations ra on ra.transaction_id = ca.transaction_id
    inner join assoc_lobbying_lobbyist al on al.entity_id = ca.entity_id
    inner join lobbying_lobbyist ll on ll.id = al.id
    inner join assoc_lobbying_client alc on alc.transaction_id = ll.transaction_id
    where
        c.cycle = 2010
        and ll.year in (2009, 2010)
    group by alc.entity_id, ca.entity_id, ra.entity_id, c.transaction_id, c.amount) x
group by client_entity, lobbyist_entity, recipient_entity;


create view tmp_org_lobbyist_contribution_overlap as
select oc.org_entity, le.name as lobbyist_name, re.name as recipient_name, lc.amount as lobbyist_amount, oc.amount as org_amount
from tmp_org_lobbyist_contributions lc
inner join tmp_org_contributions oc on 
    (lc.client_entity = oc.org_entity and lc.recipient_entity = oc.recipient_entity)
inner join matchbox_entity le on le.id = lc.lobbyist_entity
inner join matchbox_entity re on re.id = lc.recipient_entity
order by oc.org_entity, lobbyist_name, oc.amount desc, lc.amount desc;
