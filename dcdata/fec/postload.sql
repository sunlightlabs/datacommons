
drop table if exists fec_candidates;
create table fec_candidates as
select *,
    case
        when substring(candidate_id for 1) = 'P' then 'P'
        when substring(candidate_id for 1) = 'S' then 'S' || '-' || substring(candidate_id from 3 for 2)
        when substring(candidate_id for 1) = 'H' then 'H' || '-' || substring(candidate_id from 3 for 2) || '-' || current_district
    end as race
from fec_candidates_import;

create index fec_candidates_candidate_id on fec_candidates (candidate_id);

-- alter table fec_candidate_summaries alter column ending_date type date using (substring(ending_date from 5 for 4) || substring(ending_date from 1 for 2) || substring(ending_date from 3 for 2))::date; 


drop table if exists fec_indiv;
create table fec_indiv as
select fec_record, filer_id, amendment, transaction_type, contributor_lender_transfer as contributor_name, city, state, zipcode, election_type,
    regexp_replace(occupation, '/[^/]*$', '') as organization, regexp_replace(occupation, '^.*/', '') as occupation,
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount
from fec_indiv_import;
create index fec_indiv_filer_id on fec_indiv (filer_id);

drop table if exists fec_pac2cand;
create table fec_pac2cand as
select fec_record, filer_id, transaction_type, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id, candidate_id
from fec_pac2cand_import;
create index fec_pac2cand_other_id on fec_pac2cand (other_id);


drop table if exists fec_pac2pac;
create table fec_pac2pac as
select fec_record, filer_id, transaction_type, contributor_lender_transfer as contributor_name, city, state, zipcode, occupation, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id
from fec_pac2pac_import;   


drop table if exists fec_candidate_summaries;
create table fec_candidate_summaries as
select candidate_id, total_receipts, ending_cash, total_disbursements,
    candidate_loan_repayments, other_loan_repayments, refunds_to_individuals, refunds_to_committees,
    contributions_from_other_committees, contributions_from_party_committees,
    contributions_from_candidate, loans_from_candidate,
    authorized_transfers_from, total_individual_contributions,
    (substring(ending_date for 4 from 5) || substring(ending_date for 2 from 1) || substring(ending_date for 2 from 3))::date as ending_date
from fec_candidate_summaries_import;

create index fec_candidate_summaries_candidate_id on fec_candidate_summaries (candidate_id);

drop table if exists fec_committee_summaries;
create table fec_committee_summaries as
select committee_id, committee_name, committee_type, committee_designation, filing_frequency, 
    (through_year || through_month || through_day)::date as through_date,
    total_receipts, transfers_from_affiliates, individual_contributions, 
    contributions_from_other_committees, 
    total_loans_received, total_disbursements, transfers_to_affiliates
    refunds_to_individuals, refunds_to_committees, 
    loan_repayments, cash_beginning_of_year, cash_close_of_period
    debts_owed, nonfederal_transfers_received, contributions_to_committees
    independent_expenditures_made, party_coordinated_expenditures_made, nonfederal_expenditure_share
from fec_committee_summaries;
create index fec_committee_summaries_committee_id on fec_committee_summaries (committee_id);


create view agg_fec_candidate_rankings as
select candidate_id, substring(race for 1) as race,
    rank() over (partition by substring(race for 1) order by total_receipts desc) as total_receipts_rank,
    rank() over (partition by substring(race for 1) order by ending_cash desc) as cash_on_hand_rank,
    rank() over (partition by substring(race for 1) order by total_disbursements desc) as total_disbursements_rank
from fec_candidates c
inner join fec_candidate_summaries s using (candidate_id)
where
    candidate_status = 'C'
    and election_year = '12';



drop table if exists agg_fec_candidate_timeline;
create table agg_fec_candidate_timeline as
select candidate_id, race, (date - '2011-01-01') / 7 as week, count(*), sum(amount) as amount
from fec_candidates c
inner join fec_candidate_summaries s using (candidate_id)
inner join (select filer_id, date, amount from fec_indiv union all select other_id, date, amount from fec_pac2cand) t on c.committee_id = t.filer_id
where
    t.date <= s.ending_date -- there was a problem with forward-dated contributions throwing off charts 
group by candidate_id, race, week;

drop table if exists agg_fec_candidate_cumulative_timeline;
create table agg_fec_candidate_cumulative_timeline as
select candidate_id, race, week, sum(amount) OVER (partition by candidate_id, race order by week) as cumulative_raised
from agg_fec_candidate_timeline;


drop table if exists fec_candidate_itemized;
create table fec_candidate_itemized as
select
    contributor_name, date, amount, contributor_type, transaction_type, 
    organization, occupation, i.city, i.state, i.zipcode, 
    candidate_name, party_designation1 as party, race, incumbent_challenger_open as status, committee_id, candidate_id
from fec_candidates c
inner join (
    select filer_id as committee_id, 'indiv' as contributor_type, contributor_name,
        city, state, zipcode, organization, occupation,
        date, amount, transaction_type
    from fec_indiv

    union all

    select other_id, 'pac', committee_name,
        city, state, zipcode, connected_org, '',
        date, amount, transaction_type
    from fec_pac2cand t
    inner join fec_committees c on (c.committee_id = t.filer_id)) i using (committee_id);
create index fec_candidate_itemized_candidate_id on fec_candidate_itemized (candidate_id);


drop table if exists fec_committee_itemized;
create table fec_committee_itemized as
select
    contributor_name, date, amount, contributor_type, contributor_committee_id, transaction_type, 
    organization, occupation, i.city, i.state, i.zipcode, 
    committee_name, committee_id, committee_designation, committee_type, committee_party, interest_group, connected_org, candidate_id
from fec_committees c
inner join (
    select filer_id as committee_id, 'indiv' as contributor_type, contributor_name, '' as contributor_committee_id,
        city, state, zipcode, organization, occupation,
        date, amount, transaction_type
    from fec_indiv

    union all

    select filer_id, 'pac', contributor_name, other_id,
        city, state, zipcode, '', occupation,
        date, amount, transaction_type
    from fec_pac2pac) i using (committee_id);
create index fec_committee_itemized_candidate_id on fec_candidate_itemized (candidate_id);



-- these three are unfortunately not true in the data
-- alter table fec_candidates add constraint fec_candidates_committee_id foreign key (committee_id) references fec_committees (committee_id);
-- alter table fec_committees add constraint fec_committees_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);
-- alter table fec_pac2cand add constraint fec_pac2cand_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);

-- constraints are making the loading process more difficult...
-- and not sure they give us any real benefit, so considering removing them.
-- alter table fec_indiv add constraint fec_indiv_filer_id foreign key (filer_id) references fec_committees (committee_id);
-- alter table fec_pac2cand add constraint fec_pac2cand_filer_id foreign key (filer_id) references fec_committees (committee_id);
-- alter table fec_pac2pac add constraint fec_pac2pac_filer_id foreign key (filer_id) references fec_committees (committee_id);


-- used only in the "One Percent of One Percent" project
-- alter table fec_pac_summaries add column cycle integer;
-- insert into fec_pac_summaries
--     select *, 2010 from fec_pac_summaries_10
--     union all    
--     select *, 2008 from fec_pac_summaries_08
--     union all
--     select *, 2006 from fec_pac_summaries_06
--     union all
--     select *, 2004 from fec_pac_summaries_04
--     union all
--     select *, 2002 from fec_pac_summaries_02
--     union all
--     select *, 2000 from fec_pac_summaries_00
--     union all
--     select *, 1998 from fec_pac_summaries_98
--     union all
--     select *, 1996 from fec_pac_summaries_96;
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
