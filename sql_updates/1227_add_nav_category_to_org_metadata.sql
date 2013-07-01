alter table matchbox_organizationmetadata           add column is_org           boolean default('f');
alter table matchbox_organizationmetadata           add column is_pol_group     boolean default('f');


alter table organization_metadata_latest_cycle_view add column is_org           boolean default('f');
alter table organization_metadata_latest_cycle_view add column is_pol_group     boolean default('f');
