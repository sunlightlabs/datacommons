
drop index if exists earmarks_earmark_bill_ft;
drop index if exists earmarks_earmark_bill_section_ft;
drop index if exists earmarks_earmark_bill_subsection_ft;
drop index if exists earmarks_earmark_description_ft;
drop index if exists earmarks_earmark_notes_ft;

create index earmarks_earmark_bill_ft on earmarks_earmark using gin(to_tsvector('datacommons', bill));
create index earmarks_earmark_bill_section_ft on earmarks_earmark using gin(to_tsvector('datacommons', bill_section));
create index earmarks_earmark_bill_subsection_ft on earmarks_earmark using gin(to_tsvector('datacommons', bill_subsection));
create index earmarks_earmark_description_ft on earmarks_earmark using gin(to_tsvector('datacommons', description));
create index earmarks_earmark_notes_ft on earmarks_earmark using gin(to_tsvector('datacommons', notes));
    

drop index if exists earmarks_location_city_ft;    
    
create index earmarks_location_city_ft on earmarks_location using gin(to_tsvector('datacommons', city));

-- for all of the following, need to also have disjunction or coalesce or some
-- other way of searching the raw field when standardized field not available.

drop index if exists earmarks_member_name_ft;
drop index if exists earmarks_earmark_recipient_ft;

create index earmarks_member_name_ft on earmarks_member using gin(to_tsvector('datacommons', standardized_name));
create index earmarks_earmark_recipient_ft on earmarks_earmark using gin(to_tsvector('datacommons', standardized_recipient));


-- question: would indexes on the state fields be worthwhile?