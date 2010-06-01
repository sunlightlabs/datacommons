# various
drop index if exists grants_grant_assistance_type;
drop index if exists grants_grant_recipient_type;
drop index if exists grants_grant_recipient_state;

create index grants_grant_assistance_type on grants_grant (assistance_type);
create index grants_grant_recipient_type on grants_grant (recipient_type);
create index grants_grant_recipient_state on grants_grant (recipient_state);

# names
drop index if exists grants_grant_agency_name;
drop index if exists grants_grant_recipient_name;

create index grants_grant_agency_name on grants_grant (agency_name);
create index grants_grant_recipient_name on grants_grant (recipient_name);

# full-text
drop index if exists grants_grant_agency_name_ft;
drop index if exists grants_grant_recipient_name_ft;

create index grants_grant_agency_name_ft on grants_grant using gin(to_tsvector('datacommons', agency_name));
create index grants_grant_recipient_name_ft on grants_grant using gin(to_tsvector('datacommons', recipient_name));
