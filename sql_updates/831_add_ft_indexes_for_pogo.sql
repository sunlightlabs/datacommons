create index pogo_contractormisconduct__contractor_ft on pogo_contractormisconduct using gin(to_tsvector('datacommons', contractor));
create index pogo_contractormisconduct__instance_ft on pogo_contractormisconduct using gin(to_tsvector('datacommons', instance));
create index pogo_contractormisconduct__contracting_party_ft on pogo_contractormisconduct using gin(to_tsvector('datacommons', contracting_party));
create index pogo_contractormisconduct__enforcement_agency_ft on pogo_contractormisconduct using gin(to_tsvector('datacommons', enforcement_agency));
