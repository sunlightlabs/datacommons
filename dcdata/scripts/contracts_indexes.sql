drop index if exists contracts_contract_unique_transaction_id;
create index contracts_contract_unique_transaction_id on contracts_contract (unique_transaction_id);

drop index if exists contracts_contract_piid;
create index contracts_contract_piid on contracts_contract (piid);

drop index if exists contracts_contract_district;
create index contracts_contract_congressionaldistrict on contracts_contract (statecode, congressionaldistrict);

create index contracts_contract_dunsnumber on contracts_contract (dunsnumber);
create index contracts_contract_signeddate on contracts_contract (signeddate);

drop index if exists contracts_contract_fiscal_year;
create index contracts_contract_fiscal_year on contracts_contract (fiscal_year);

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

-- default sort order from API
drop index if exists contracts_contract_defaultsort;
create index contracts_contract_defaultsort on contracts_contract (fiscal_year desc, obligatedamount desc);