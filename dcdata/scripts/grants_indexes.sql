

-- full-text
drop index if exists grants_grant_agency_name_ft;
drop index if exists grants_grant_recipient_name_ft;

create index grants_grant_agency_name_ft on grants_grant using gin(to_tsvector('datacommons', agency_name));
create index grants_grant_recipient_name_ft on grants_grant using gin(to_tsvector('datacommons', recipient_name));

create index grants_grant_total_funding_amount on grants_grant (total_funding_amount);