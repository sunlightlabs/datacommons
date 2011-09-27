drop index if exists faca_records_org_id;
drop index if exists faca_records_agency_abbr_ft;
drop index if exists faca_records_agency_name_ft;
drop index if exists faca_records_committee_name_ft;
drop index if exists faca_records_member_name_ft;
drop index if exists faca_records_affiliation_ft;

delete from faca_records;
    
insert into faca_records 
    (agency_abbr, agency_name, committee_name, committee_url, member_name, member_firstlast, affiliation, 
    chair, org_name, org_id, appointment_type, appointment_term, pay_plan,
    pay_source, member_designation, represented_group, start_date, end_date)
select 
    AgencyAbbr as agency_abbr, 
    AgencyName as agency_name, 
    CommitteeName as committee_name,
    case when CommitteeURL is null then '' else CommitteeURL end as committee_url,
    replace(m.FirstName || ' ' || (case when m.MiddleName != '' then m.MiddleName || ' ' else '' end) || m.LastName, '.', '') as member_name, 
    replace(m.FirstName || ' ' || m.LastName, '.', '') as member_firstlast, 
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
left join faca_generalinformation g using (CID)
left join faca_matches using (MembersID)
left join matchbox_entity e on entity_id = e.id
group by 
    AgencyAbbr, 
    AgencyName, 
    CommitteeName, 
    case when CommitteeURL is null then '' else CommitteeURL end,
    replace(m.FirstName || ' ' || (case when m.MiddleName != '' then m.MiddleName || ' ' else '' end) || m.LastName, '.', ''),
    replace(m.FirstName || ' ' || m.LastName, '.', ''),
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


drop table if exists agg_faca_records;

create table agg_faca_records as
with faca_most_recent as 
    (select 
        org_id, agency_abbr, agency_name, committee_name, member_firstlast,
        first_value(committee_url) over committee_window as committee_url,
        first_value(chair) over member_window as chair,
        first_value(affiliation) over member_window as affiliation, 
        start_date, 
        end_date
    from faca_records
    window 
        member_window as (partition by org_id, agency_abbr, agency_name, committee_name, member_firstlast order by end_date desc),
        committee_window as (partition by org_id, agency_abbr, agency_name, committee_name order by end_date desc))
select org_id, agency_abbr, agency_name, committee_name, committee_url, member_firstlast, chair, affiliation, min(start_date) as start_date, max(end_date) as end_date
from faca_most_recent
group by org_id, agency_abbr, agency_name, committee_name, committee_url, member_firstlast, chair, affiliation;

create index agg_faca_records_org_idx on agg_faca_records (org_id);
create index agg_faca_records_agency_org_idx on agg_faca_records(org_id, agency_abbr);
