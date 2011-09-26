drop table if exists tmp_most_recent_report_ids;
create table tmp_most_recent_report_ids as
    select distinct
        on (committee_fec_id, start_date, end_date)
        file_num
    from
        contribution_bundle
    order by committee_fec_id, start_date, end_date, filing_date desc
;

update contribution_bundle set should_ignore = 't' where file_num not in (select file_num from tmp_most_recent_report_ids);
update contribution_bundle set should_ignore = 'f' where file_num in (select file_num from tmp_most_recent_report_ids);

drop table if exists tmp_overlapping_or_amended_bundles;
create table tmp_overlapping_or_amended_bundles as
    select
        a.committee_fec_id,
        a.file_num as file_num_a,
        a.start_date as start_date_a,
        a.end_date as end_date_a,
        a.filing_date as filing_date_a,
        a.is_amendment as is_amendment_a,
        b.file_num as file_num_b,
        b.start_date as start_date_b,
        b.end_date as end_date_b,
        b.filing_date as filing_date_b,
        b.is_amendment as is_amendment_b
    from
        contribution_bundle a
        inner join contribution_bundle b using (committee_fec_id)
    where
        not a.should_ignore and not b.should_ignore
        and a.committee_fec_id = b.committee_fec_id
        and a.file_num != b.file_num
        and (b.filing_date > a.filing_date or (b.is_amendment and b.filing_date = a.filing_date))
        and (a.start_date, a.end_date) overlaps (b.start_date, b.end_date)
;

-- TODO: check if this is coming out right
update contribution_bundle cb
set supercedes_id = file_num_a
from tmp_overlapping_or_amended_bundles o
where o.file_num_b = cb.file_num
;
update contribution_bundle cb
set should_ignore = 't'
from tmp_overlapping_or_amended_bundles o
where o.file_num_a = cb.file_num
;


drop table if exists assoc_bundle_recipients;
create table assoc_bundle_recipients as
    select
        file_num,
        entity_id
    from
        contribution_bundle
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


drop table if exists assoc_bundler_firms;
create table assoc_bundler_firms as
select b.id as bundle_id, entity_id
from contribution_lobbyistbundle b
inner join assoc_bundler_matches_manual a on
    b.name = a.name or b.employer = a.name
inner join matchbox_entity e on e.id = a.entity_id
where
    e.type = 'organization'
group by b.id, entity_id;


drop table if exists assoc_bundler_lobbyists;
create table assoc_bundler_lobbyists as
select b.id as bundle_id, entity_id
from contribution_lobbyistbundle b
inner join assoc_bundler_matches_manual a on
    b.name = a.name
inner join matchbox_entity e on e.id = a.entity_id
where
    e.type = 'individual'
group by b.id, entity_id;


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
    sum(amount) as amount
from contribution_bundle cb
inner join contribution_lobbyistbundle lb on cb.file_num = lb.file_num_id
left join assoc_bundle_recipients ra on ra.file_num = cb.file_num
left join matchbox_entity re on re.id = ra.entity_id
left join assoc_bundler_firms fa on fa.bundle_id = lb.id
left join matchbox_entity fe on fe.id = fa.entity_id
left join assoc_bundler_lobbyists la on la.bundle_id = lb.id
left join matchbox_entity le on le.id = la.entity_id
where
    not cb.should_ignore
group by
    re.id, coalesce(re.name, cb.committee_name),
    fe.id , coalesce(fe.name, lb.name),
    le.id, coalesce(le.name, lb.name),
    case when report_year % 2 = 0 then report_year else report_year + 1 end;


