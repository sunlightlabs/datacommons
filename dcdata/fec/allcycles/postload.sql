
create view fec_candidates_allcycles_import as
    select 2012 as cycle, * from fec_candidates_12
union all
    select 2010, * from fec_candidates_10
union all
    select 2008, * from fec_candidates_08
union all
    select 2006, * from fec_candidates_06
union all
    select 2004, * from fec_candidates_04
union all
    select 2002, * from fec_candidates_02
union all
    select 2000, * from fec_candidates_00;

drop table if exists fec_candidates_allcycles;
create table fec_candidates_allcycles as
select *,
    case
        when substring(candidate_id for 1) = 'P' then 'P'
        when substring(candidate_id for 1) = 'S' then 'S' || '-' || substring(candidate_id from 3 for 2)
        when substring(candidate_id for 1) = 'H' then 'H' || '-' || substring(candidate_id from 3 for 2) || '-' || current_district
    end as race
from fec_candidates_allcycles_import;

create index fec_candidates_allcycles_candidate_id on fec_candidates_allcycles (candidate_id);


create view fec_committees_allcycles as
    select 2012 as cycle, * from fec_committees_12
union all
    select 2010, * from fec_committees_10
union all
    select 2008, * from fec_committees_08
union all
    select 2006, * from fec_committees_06
union all
    select 2004, * from fec_committees_04
union all
    select 2002, * from fec_committees_02
union all
    select 2000, * from fec_committees_00;


create view fec_indiv_allcycles_import as
    select 2012 as cycle, * from fec_indiv_12
union all
    select 2010, * from fec_indiv_10
union all
    select 2008, * from fec_indiv_08
union all
    select 2006, * from fec_indiv_06
union all
    select 2004, * from fec_indiv_04
union all
    select 2002, * from fec_indiv_02
union all
    select 2000, * from fec_indiv_00;

drop table if exists fec_indiv_allcycles;
create table fec_indiv_allcycles as
select cycle, fec_record, filer_id, amendment, transaction_type, contributor_lender_transfer as contributor_name, city, state, zipcode, election_type,
    regexp_replace(occupation, '/[^/]*$', '') as organization, regexp_replace(occupation, '^.*/', '') as occupation,
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount
from fec_indiv_allcycles_import;
create index fec_indiv_allcycles_filer_id on fec_indiv_allcycles (filer_id);


create view fec_pac2cand_allcycles_import as
    select 2012 as cycle, * from fec_pac2cand_12
union all
    select 2010, * from fec_pac2cand_10
union all
    select 2008, * from fec_pac2cand_08
union all
    select 2006, * from fec_pac2cand_06
union all
    select 2004, * from fec_pac2cand_04
union all
    select 2002, * from fec_pac2cand_02
union all
    select 2000, * from fec_pac2cand_00;

drop table if exists fec_pac2cand_allcycles;
create table fec_pac2cand_allcycles as
select cycle, fec_record, filer_id, transaction_type, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id, candidate_id
from fec_pac2cand_allcycles_import;

create index fec_pac2cand_allcycles_filer_id on fec_pac2cand_allcycles (filer_id);
create index fec_pac2cand_allcycles_other_id on fec_pac2cand_allcycles (other_id);
create index fec_pac2cand_allcycles_candidate_id on fec_pac2cand_allcycles (candidate_id);
    

create view fec_pac2pac_allcycles_import as
    select 2012 as cycle, * from fec_pac2pac_12
union all
    select 2010, * from fec_pac2pac_10
union all
    select 2008, * from fec_pac2pac_08
union all
    select 2006, * from fec_pac2pac_06
union all
    select 2004, * from fec_pac2pac_04
union all
    select 2002, * from fec_pac2pac_02
union all
    select 2000, * from fec_pac2pac_00;

drop table if exists fec_pac2pac_allcycles;
create table fec_pac2pac_allcycles as
select cycle, fec_record, filer_id, transaction_type, contributor_lender_transfer as contributor_name, city, state, zipcode, occupation, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id
from fec_pac2pac_allcycles_import;

create index fec_pac2pac_allcycles_filer_id on fec_pac2pac_allcycles (filer_id);
create index fec_pac2pac_allcycles_other_id on fec_pac2pac_allcycles (other_id);


create view fec_committee_summaries_allcycles_import as
    select 2012 as cycle, * from fec_pac_summaries_12
    union all
    select 2010, * from fec_pac_summaries_10
    union all 
    select 2008, * from fec_pac_summaries_08
    union all 
    select 2006, * from fec_pac_summaries_06
    union all 
    select 2004, * from fec_pac_summaries_04
    union all 
    select 2002, * from fec_pac_summaries_02
    union all 
    select 2000, * from fec_pac_summaries_00;
    
create table fec_committee_summaries_allcycles as
select cycle, committee_id, committee_name, committee_type, committee_designation, filing_frequency, 
    (through_year || through_month || through_day)::date as through_date,
    total_receipts, transfers_from_affiliates, individual_contributions, 
    contributions_from_other_committees, 
    total_loans_received, total_disbursements, transfers_to_affiliates,
    refunds_to_individuals, refunds_to_committees, 
    loan_repayments, cash_beginning_of_year, cash_close_of_period,
    debts_owed, nonfederal_transfers_received, contributions_to_committees,
    independent_expenditures_made, party_coordinated_expenditures_made, nonfederal_expenditure_share
from fec_committee_summaries_allcycles_import
where
    -- there are a number of data-less rows. Discard them by looking for valid date.
    through_year != 0;




    
--     
-- alter table fec_candidate_summaries add column cycle integer;
-- insert into fec_candidate_summaries
--     select *, 2010 from fec_candidate_summaries_10
--     union all
--     select *, 2008 from fec_candidate_summaries_08
--     union all
--     select *, 2006 from fec_candidate_summaries_06
--     union all
--     select *, 2004 from fec_candidate_summaries_04
--     union all
--     select *, 2002 from fec_candidate_summaries_02
--     union all
--     select *, 2000 from fec_candidate_summaries_00
--     union all
--     select *, 1998 from fec_candidate_summaries_98
--     union all
--     select *, 1996 from fec_candidate_summaries_96;
