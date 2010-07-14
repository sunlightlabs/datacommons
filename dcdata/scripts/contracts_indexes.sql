# names
drop index if exists contracts_contract_agency_name;
drop index if exists contracts_contract_contracting_agency_name;
drop index if exists contracts_contract_requesting_agency_name;
drop index if exists contracts_contract_vendor_city;
drop index if exists contracts_contract_vendor_name;

create index contracts_contract_agency_name on contracts_contract (agency_name);
create index contracts_contract_contracting_agency_name on contracts_contract (contracting_agency_name);
create index contracts_contract_requesting_agency_name on contracts_contract (requesting_agency_name);
create index contracts_contract_vendor_city on contracts_contract (vendor_city);
create index contracts_contract_vendor_name on contracts_contract (vendor_name);

# full-text
drop index if exists contracts_contract_agency_name_ft;
drop index if exists contracts_contract_contracting_agency_name_ft;
drop index if exists contracts_contract_requesting_agency_name_ft;
drop index if exists contracts_contract_vendor_city_ft;
drop index if exists contracts_contract_vendor_name_ft;

create index contracts_contract_agency_name_ft on contracts_contract using gin(to_tsvector('datacommons', agency_name));
create index contracts_contract_contracting_agency_name_ft on contracts_contract using gin(to_tsvector('datacommons', contracting_agency_name));
create index contracts_contract_requesting_agency_name_ft on contracts_contract using gin(to_tsvector('datacommons', requesting_agency_name));
create index contracts_contract_vendor_city_ft on contracts_contract using gin(to_tsvector('datacommons', vendor_city));
create index contracts_contract_vendor_name_ft on contracts_contract using gin(to_tsvector('datacommons', vendor_name));