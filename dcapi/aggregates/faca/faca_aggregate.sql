drop table faca_records;

-- think I can change the original schema to use varchar rather than char, and the the trims shouldn't be needed

create table faca_records as
select 
    trim(AgencyAbbr) as AgencyAbbr, 
    trim(AgencyName) as AgencyName, 
    trim(CommitteeName) as CommitteeName, 
    trim(m.FirstName) || ' ' || trim(m.MiddleName) || ' ' || trim(m.LastName) as MemberName, 
    trim(OccupationOrAffiliation) as affiliation, 
    e.name as org_name, 
    e.id as org_id,
    -1 as cycle,
    min(case when StartDate = '' then null else StartDate::timestamp end), 
    max(case when EndDate = '' then null else EndDate::timestamp end), 
    count(*)
from faca_committees
inner join faca_agencies using (AID)
inner join faca_members m using (CID)
left join faca_matches using (MembersID)
left join matchbox_entity e on entity_id = e.id
group by 
    trim(AgencyAbbr), 
    trim(AgencyName), 
    trim(CommitteeName), 
    trim(m.FirstName) || ' ' || trim(m.MiddleName) || ' ' || trim(m.LastName), 
    trim(OccupationOrAffiliation), 
    e.name, 
    e.id;
    
create index faca_records_org_id on faca_records (org_id);

