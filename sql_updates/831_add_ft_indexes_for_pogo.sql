create index pogo_contractor__name_ft on pogo_contractor using gin(to_tsvector('datacommons', name));
create index pogo_misconduct__instance_ft on pogo_misconduct using gin(to_tsvector('datacommons', instance));
create index pogo_misconduct__contracting_party_ft on pogo_misconduct using gin(to_tsvector('datacommons', contracting_party));
create index pogo_misconduct__enforcement_agency_ft on pogo_misconduct using gin(to_tsvector('datacommons', enforcement_agency));
