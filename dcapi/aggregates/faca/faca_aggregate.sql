drop index if exists faca_records_org_id;
drop index if exists faca_records_agency_abbr_ft;
drop index if exists faca_records_agency_name_ft;
drop index if exists faca_records_committee_name_ft;
drop index if exists faca_records_member_name_ft;
drop index if exists faca_records_affiliation_ft;

delete from faca_records;
    
-- think I can change the original schema to use varchar rather than char, and the the trims shouldn't be needed
-- grouping on affiliation be problematic: sometimes the same person is listed with slight variants in affliation in different years.
--      I think we can rely on names being unique within a particular committee. So should really use the most common affliation string.
--          on the other hand, what about when there's been a significant title change...maybe we do want to show that.

insert into faca_records 
    (agency_abbr, agency_name, committee_name, member_name, affiliation, 
    chair, org_name, org_id, appointment_type, appointment_term, pay_plan,
    pay_source, member_designation, represented_group, start_date, end_date)
select 
    AgencyAbbr as agency_abbr, 
    AgencyName as agency_name, 
    CommitteeName as committee_name, 
    replace(m.FirstName || ' ' || m.MiddleName || ' ' || m.LastName, '.', '') as member_name, 
    OccupationOrAffiliation as affiliation,
    Chairperson = 'Yes' chair, 
    e.name as org_name, 
    e.id as org_id,
    AppointmentType as appointment_type,
	AppointmentTerm as appointment_term,
	PayPlan as pay_plan,
	PaySource as pay_source,
	MemberDesignation as member_designation,
	RepresentedGroup as represented_group,
    min(case when StartDate = '' then null else StartDate::timestamp end) as start_date, 
    max(case when EndDate = '' then null else EndDate::timestamp end) as end_date
from faca_committees
inner join faca_agencies using (AID)
inner join faca_members m using (CID)
left join faca_matches using (MembersID)
left join matchbox_entity e on entity_id = e.id
group by 
    AgencyAbbr, 
    AgencyName, 
    CommitteeName, 
    m.FirstName || ' ' || m.MiddleName || ' ' || m.LastName, 
    OccupationOrAffiliation,
    Chairperson = 'Yes',
    e.name, 
    e.id,
    AppointmentType,
	AppointmentTerm,
	PayPlan,
	PaySource,
	MemberDesignation,
	RepresentedGroup;
    
create index faca_records_org_id on faca_records (org_id);
create index faca_records_agency_abbr_ft on faca_records using gin(to_tsvector('datacommons', agency_abbr));
create index faca_records_agency_name_ft on faca_records using gin(to_tsvector('datacommons', agency_name));
create index faca_records_committee_name_ft on faca_records using gin(to_tsvector('datacommons', committee_name));
create index faca_records_member_name_ft on faca_records using gin(to_tsvector('datacommons', member_name));
create index faca_records_affiliation_ft on faca_records using gin(to_tsvector('datacommons', affiliation));

        