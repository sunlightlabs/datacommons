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

-- NOTE: The table below, right now, is matchbox_committeerecipient (committee_id, entity_id)
-- QUESTIONS: What do committee recipients look like? What type of entity (politicions, other committees)
-- are they, and do they change over time? Do we need to key them by cycle or file_num?
-- The command to build this table is:
-- insert into matchbox_committeerecipient (committee_id, entity_id) select distinct c.id, entity_id from contribution_contribution ctb inner join recipient_associations using (transaction_id) inner join matchbox_committee c on ctb.committee_ext_id = c.fec_id where ctb.contributor_type = 'C' and cycle >= 2008 and transaction_namespace = 'urn:fec:transaction' and recipient_type in ('P', 'C');

--create table assoc_bundle_committee_to_recipient as
--    select distinct
--        committee_ext_id,
--        entity_id
--    from
--        contribution_contribution
--        inner join recipient_associations using (transaction_id)
--;

create table assoc_bundle_recipients as
    select
        file_num as report_id,
        entity_id as recipient_entity_id
    from
        contribution_bundle
        inner join matchbox_committee on committee_fec_id = fec_id
        inner join matchbox_committeerecipient using (committee_id)
;

-- this is the query that's having trouble finishing.
--insert into matchbox_committeerecipient (committee_id, entity_id) select distinct c.id, entity_id from contribution_contribution ctb inner join recipient_associations using (transaction_id) inner join matchbox_committee c on ctb.committee_ext_id = c.fec_id where ctb.contributor_type = 'C' and cycle >= 2008 and transaction_namespace = 'urn:fec:transaction' and recipient_type in ('P', 'C');


create table assoc_bundle_donors as
    select
        id as bundle_id,
        le.id as lobbyist_entity_id,
        lfe.id as lobbying_firm_entity_id
    from
        contribution_lobbyistbundle lb
        -- it would be nice if the table below looked more like assoc_bundler_lobbyist_donor
        left join bundler_lobbyist_matches_curated lmc on lb.id = lmc.subject_id
        -- this table (or similar) has yet to be created
        left join assoc_bundle_lobbyist_employer lfe on lmc.id = lfe.id
;


