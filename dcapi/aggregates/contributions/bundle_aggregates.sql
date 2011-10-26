drop function if exists semi_annual(date) cascade;
create function semi_annual(date) returns text as $$
    select extract(year from $1)::text || '/' || case when extract(month from $1) > 6 then '1' else '0' end
$$ language SQL;

create view contribution_bundle_latest as
select distinct on (committee_fec_id, semi_annual(end_date)) * 
from contribution_bundle
order by committee_fec_id, semi_annual(end_date),  end_date desc, filing_date desc;



drop table if exists assoc_bundle_recipients cascade;
create table assoc_bundle_recipients as
    select
        file_num,
        entity_id
    from
        contribution_bundle_latest
        inner join contribution_committee on committee_fec_id = committee_id
        inner join matchbox_entityattribute on recipient_id = value
    where
        namespace = 'urn:crp:recipient';


-- uncomment these lines to re-import the manual validations

-- drop table if exists assoc_bundler_matches_manual;
-- create table assoc_bundler_matches_manual (
--     name varchar(255),
--     entity_id uuid
-- );
-- \copy assoc_bundler_matches_manual from bundler_matches.csv csv header

-- note: the recipients table above uses file_num, but these below use the id PK
-- should probably pick one and fix it to be consistent

-- the contribution_committee table is missing from staging, preventing
-- these aggregates from loading properly


drop table if exists assoc_bundler_firms;
create table assoc_bundler_firms as
select lb.id as bundle_id, entity_id
from contribution_bundle_latest cb -- this table here only to restrict which lobbyistbundles are used.
inner join contribution_lobbyistbundle lb on 
    cb.file_num = lb.file_num_id
inner join assoc_bundler_matches_manual a on
    lb.name = a.name or lb.employer = a.name
inner join matchbox_entity e on e.id = a.entity_id
where
    e.type = 'organization'
group by lb.id, entity_id;


drop table if exists assoc_bundler_lobbyists;
create table assoc_bundler_lobbyists as
select lb.id as bundle_id, entity_id
from contribution_bundle_latest cb -- this table here only to restrict which lobbyistbundles are used.
inner join contribution_lobbyistbundle lb on 
    cb.file_num = lb.file_num_id
inner join assoc_bundler_matches_manual a on
    lb.name = a.name
inner join matchbox_entity e on e.id = a.entity_id
where
    e.type = 'individual'
group by lb.id, entity_id;


drop table if exists agg_bundling;
create table agg_bundling as
select
    re.id                                as recipient_id,
    coalesce(re.name, cb.committee_name) as recipient_name,
    fe.id                                as firm_id,
    coalesce(fe.name, lb.name)           as firm_name,
    le.id                                as lobbyist_id,
    coalesce(le.name, lb.name)           as lobbyist_name,
    case when report_year % 2 = 0 then report_year else report_year + 1 end as cycle,
    sum(coalesce(lb.semi_annual_amount, amount)) as amount
from contribution_bundle_latest cb
inner join contribution_lobbyistbundle lb on cb.file_num = lb.file_num_id
left join assoc_bundle_recipients ra on ra.file_num = cb.file_num
left join matchbox_entity re on re.id = ra.entity_id
left join assoc_bundler_firms fa on fa.bundle_id = lb.id
left join matchbox_entity fe on fe.id = fa.entity_id
left join assoc_bundler_lobbyists la on la.bundle_id = lb.id
left join matchbox_entity le on le.id = la.entity_id
group by
    re.id, coalesce(re.name, cb.committee_name),
    fe.id , coalesce(fe.name, lb.name),
    le.id, coalesce(le.name, lb.name),
    case when report_year % 2 = 0 then report_year else report_year + 1 end;

