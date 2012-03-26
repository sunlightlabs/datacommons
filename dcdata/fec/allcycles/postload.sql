
-- used only in the "One Percent of One Percent" project
-- alter table fec_pac_summaries add column cycle integer;
create table fec_committee_summaries_allcycles_import as
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
