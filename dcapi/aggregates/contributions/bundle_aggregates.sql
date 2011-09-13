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
