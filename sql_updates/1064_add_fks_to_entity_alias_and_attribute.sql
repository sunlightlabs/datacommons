alter table matchbox_entityattribute add foreign key (entity_id) references matchbox_entity (id);
alter table matchbox_entityalias add foreign key (entity_id) references matchbox_entity (id);
