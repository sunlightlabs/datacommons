alter table matchbox_entity add column should_delete boolean default('f');
alter table matchbox_entity alter column should_delete set not null;
alter table matchbox_entity add column flagged_on timestamp;

