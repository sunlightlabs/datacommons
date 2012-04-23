-- we should have separate indexes, not multi-column ones
create index matchbox_politicianmetadata__entity_id on matchbox_politicianmetadata (entity_id);
create index matchbox_politicianmetadata__cycle on matchbox_politicianmetadata (cycle);
create unique index matchbox_politicianmetadata__entity_id__cycle__unq on matchbox_politicianmetadata (entity_id, cycle);
drop index matchbox_politicianmetadata_entity_id_key; -- this was entity_id, cycle together, without including a unique constraint
