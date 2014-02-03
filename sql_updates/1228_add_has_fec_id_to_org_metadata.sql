alter table matchbox_organizationmetadata           add column has_fec_profile  boolean default('f');

alter table organization_metadata_latest_cycle_view add column has_fec_profile  boolean default('f');
