

create table tmp_attributes_to_delete as
select value
from matchbox_entityattribute a
inner join fec_committees c1 on committee_id = value
where
    namespace = 'urn:fec:committee'
    and committee_type = 'O'
    and exists (
        select *
        from matchbox_entityattribute b
        inner join fec_committees c2 on c2.committee_id = b.value
        where
            a.entity_id = b.entity_id
            and b.namespace = 'urn:fec:committee'
            and a.value != b.value
            and c2.committee_type != 'O'
    );

begin;

delete from matchbox_entityattribute where value in (table tmp_attributes_to_delete);


drop table if exists tmp_entities_to_create;
create table tmp_entities_to_create as
select committee_name, committee_id
from fec_committee_summaries
where
    committee_type = 'O'
    and not exists (
        select *
        from matchbox_entityattribute
        where
            namespace = 'urn:fec:committee'
            and value = committee_id
    );
    
\copy tmp_entities_to_create to new_entities.csv csv 


-- # create entities with the following script
-- import csv
-- from dcentity.entity import build_entity
-- from django.db import transaction
-- 
-- with transaction.commit_on_success():
--     for (name, id) in csv.reader(open('new_entities.csv', 'r')):
--         build_entity(name, 'organization', [('urn:fec:committee', id)])


rollback;



alter table matchbox_organizationmetadata add column is_superpac boolean not null default false;

update matchbox_organizationmetadata
set is_superpac = true
from matchbox_entityattribute a
inner join fec_committees on committee_id = value
where
    matchbox_organizationmetadata.entity_id = a.entity_id
    and matchbox_organizationmetadata.cycle = 2012
    and namespace = 'urn:fec:committee'
    and committee_type = 'O';


insert into matchbox_organizationmetadata (entity_id, cycle, is_superpac)
select entity_id, 2012, true
from matchbox_entityattribute a
inner join fec_committees on committee_id = value
where
    namespace = 'urn:fec:committee'
    and committee_type = 'O'
    and not exists (
        select *
        from matchbox_organizationmetadata existing
        where
            existing.entity_id = a.entity_id
            and existing.cycle = 2012
    );



-- add the org-> SuperPAC links

-- first, load tmp_crp_committees, as done in crp_load_fec_ids command

insert into matchbox_superpaclinks (superpac_entity_id, controlling_org_entity_id)
select a.entity_id, l.entity_id
from tmp_crp_committees c
inner join matchbox_entityattribute a on a.namespace = 'urn:fec:committee' and c.CmteID = a.value
inner join fec_committees f on f.committee_id = a.value
inner join matchbox_entityalias l on lower(alias) = lower(c.ultorg)
where
    a.entity_id != l.entity_id
    and f.committee_type = 'O'
    and not exists (
        select *
        from matchbox_superpaclinks existing
        where
            existing.superpac_entity_id = a.entity_id
            and existing.controlling_org_entity_id = l.entity_id
    );
