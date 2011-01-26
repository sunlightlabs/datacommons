-- full-text
drop index if exists contracts_contract_agency_name_ft;
drop index if exists contracts_contract_contracting_agency_name_ft;
drop index if exists contracts_contract_requesting_agency_name_ft;
drop index if exists contracts_contract_vendor_city_ft;
drop index if exists contracts_contract_vendor_name_ft;

create index contracts_contract_agency_name_ft on contracts_contract using gin(to_tsvector('datacommons', agency_name));
create index contracts_contract_contracting_agency_name_ft on contracts_contract using gin(to_tsvector('datacommons', contracting_agency_name));
create index contracts_contract_requesting_agency_name_ft on contracts_contract using gin(to_tsvector('datacommons', requesting_agency_name));
create index contracts_contract_vendor_city_ft on contracts_contract using gin(to_tsvector('datacommons', city));
create index contracts_contract_vendor_name_ft on contracts_contract using gin(to_tsvector('datacommons', vendorname));