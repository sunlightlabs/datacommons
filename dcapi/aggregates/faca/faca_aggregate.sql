drop table faca_records;

-- think I can change the original schema to use varchar rather than char, and the the trims shouldn't be needed
-- grouping on affiliation be problematic: sometimes the same person is listed with slight variants in affliation in different years.
--      I think we can rely on names being unique within a particular committee. So should really use the most common affliation string.
--          on the other hand, what about when there's been a significant title change...maybe we do want to show that.

create table faca_records as
select 
    AgencyAbbr as AgencyAbbr, 
    AgencyName as AgencyName, 
    CommitteeName as CommitteeName, 
    replace(m.FirstName || ' ' || m.MiddleName || ' ' || m.LastName, '.', '') as MemberName, 
    OccupationOrAffiliation as affiliation,
    Chairperson = 'Yes' Chair, 
    e.name as org_name, 
    e.id as org_id,
    AppointmentType,
	AppointmentTerm,
	PayPlan,
	PaySource,
	MemberDesignation,
	RepresentedGroup,
    min(case when StartDate = '' then null else StartDate::timestamp end) as StartDate, 
    max(case when EndDate = '' then null else EndDate::timestamp end) as EndDate,
    count(*)
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

