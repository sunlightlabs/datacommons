drop table if exists fec_candidates;
create table fec_candidates as
select *,
    case
        when office = 'P' then 'P'
        when office = 'S' then 'S' || '-' || office_state
        when office = 'H' then 'H' || '-' || office_state || '-' || office_district
    end as race
from fec_candidates_import;

create index fec_candidates_candidate_id on fec_candidates (candidate_id);


drop table if exists fec_indiv;
create table fec_indiv as
select 
    filer_id,
    amendment,
    report_type,
    election_type,
    microfilm_location,
    lower(transaction_type) as transaction_type,
    entity_type,
    contributor_name,
    city,
    state,
    zipcode,
    employer,
    occupation,
    (substring(date for 4 from 5) || substring(date for 2) || substring(date for 2 from 3))::date as date,
    case when transaction_type = '22Y' then -abs(amount) else amount end as amount,
    other_id,
    transaction_id,
    file_num,
    memo_code,
    memo_text,
    fec_record
from fec_indiv_import;
create index fec_indiv_filer_id on fec_indiv (filer_id);

drop table if exists fec_pac2cand;
create table fec_pac2cand as
select 
    filer_id,
    amendment,
    report_type,
    election_type,
    microfilm_location,
    lower(transaction_type) as transaction_type,
    entity_type,
    contributor_name,
    city,
    state,
    zipcode,
    employer,
    occupation,
    (substring(date for 4 from 5) || substring(date for 2) || substring(date for 2 from 3))::date as date,
    case when transaction_type = '22Z' then -abs(amount) else amount end as amount,
    other_id,
    candidate_id,
    transaction_id,
    file_num,
    memo_code,
    memo_text,
    fec_record
from fec_pac2cand_import;
create index fec_pac2cand_other_id on fec_pac2cand (other_id);
create index fec_pac2cand_cand_id on fec_pac2cand (candidate_id);

drop table if exists fec_pac2pac;
create table fec_pac2pac as
select 
    filer_id,
    amendment,
    report_type,
    election_type,
    microfilm_location,
    lower(transaction_type) as transaction_type,
    entity_type,
    contributor_name,
    city,
    state,
    zipcode,
    employer,
    occupation,
    (substring(date for 4 from 5) || substring(date for 2) || substring(date for 2 from 3))::date as date,
    case when transaction_type = '22Z' then -abs(amount) else amount end as amount,
    other_id,
    transaction_id,
    file_num,
    memo_code,
    memo_text,
    fec_record
from fec_pac2pac_import;   
create index fec_pac2pac_filer_id on fec_pac2pac (filer_id);
create index fec_pac2pac_other_id on fec_pac2pac (other_id);



drop table if exists agg_fec_candidate_rankings;
create table agg_fec_candidate_rankings as
select candidate_id, office,
    rank() over (partition by office order by total_receipts desc) as total_receipts_rank,
    rank() over (partition by office order by ending_cash desc) as cash_on_hand_rank,
    rank() over (partition by office order by total_disbursements desc) as total_disbursements_rank
from fec_candidates c
inner join fec_candidate_summaries s using (candidate_id)
where
    candidate_status = 'C'
    and election_year = '2012';



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
    employer, occupation, i.city, i.state, i.zipcode, 
    candidate_name, party, race, incumbent_challenger_open as status, committee_id, candidate_id
from fec_candidates c
inner join (
    select filer_id as committee_id, 'indiv' as contributor_type, contributor_name,
        i.city, i.state, i.zipcode, employer, occupation,
        date, amount, transaction_type
    from fec_indiv i

    union all

    select other_id, 'pac', committee_name,
        t.city, t.state, t.zipcode, connected_org, '',
        date, amount, transaction_type
    from fec_pac2cand t
    inner join fec_committees c on (c.committee_id = t.filer_id)) i using (committee_id);
create index fec_candidate_itemized_candidate_id on fec_candidate_itemized (candidate_id);


drop table if exists fec_committee_itemized;
create table fec_committee_itemized as
select
    contributor_name, date, amount, contributor_type, contributor_committee_id, transaction_type, 
    employer, occupation, i.city, i.state, i.zipcode, 
    committee_name, committee_id, committee_designation, committee_type, committee_party, interest_group, connected_org, candidate_id
from fec_committees c
inner join (
    select filer_id as committee_id, 'indiv' as contributor_type, contributor_name, '' as contributor_committee_id,
        city, state, zipcode, employer, occupation,
        date, amount, transaction_type
    from fec_indiv

    union all

    select filer_id, 'pac', contributor_name, other_id,
        city, state, zipcode, '', occupation,
        date, amount, transaction_type
    from fec_pac2pac) i using (committee_id)
where
    -- only transaction types 10-19 are money coming in. 20-29 are money going out, which we're not interested in here.
    substring(transaction_type for 2)::integer between 10 and 19;
create index fec_committee_itemized_committee_id on fec_committee_itemized (committee_id);


drop table if exists agg_fec_committee_summaries;
create table agg_fec_committee_summaries as
select
    cycle, entity_id,
    sum(total_receipts - (loan_repayments + refunds_to_individuals + refunds_to_committees)) as total_raised,
    sum(individual_contributions - refunds_to_individuals) as individual_contributions,
    sum(contributions_from_other_committees) as contributions_from_other_committees,
    sum(transfers_from_affiliates) as transfers_from_affiliates,
    sum(nonfederal_transfers_received) as nonfederal_transfers_received,
    sum(total_loans_received) as total_loans_received,
    sum(total_disbursements) as total_disbursements,
    sum(cash_close_of_period) as cash_close_of_period,
    sum(debts_owed) as debts_owed,
    sum(contributions_to_committees) as contributions_to_committees,
    sum(independent_expenditures_made) as independent_expenditures_made,
    sum(party_coordinated_expenditures_made) as party_coordinated_expenditures_made,
    sum(nonfederal_expenditure_share) as nonfederal_expenditure_share,
    min(through_date) as min_through_date,
    max(through_date) as max_through_date,
    count(*)
from fec_committee_summaries c
inner join matchbox_entityattribute a on c.committee_id = a.value and a.namespace = 'urn:fec:committee'
cross join (values (-1), (2012)) as cycles (cycle)
group by cycle, entity_id;



-- these three are unfortunately not true in the data
-- alter table fec_candidates add constraint fec_candidates_committee_id foreign key (committee_id) references fec_committees (committee_id);
-- alter table fec_committees add constraint fec_committees_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);
-- alter table fec_pac2cand add constraint fec_pac2cand_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);

-- constraints are making the loading process more difficult...
-- and not sure they give us any real benefit, so considering removing them.
-- alter table fec_indiv add constraint fec_indiv_filer_id foreign key (filer_id) references fec_committees (committee_id);
-- alter table fec_pac2cand add constraint fec_pac2cand_filer_id foreign key (filer_id) references fec_committees (committee_id);
-- alter table fec_pac2pac add constraint fec_pac2pac_filer_id foreign key (filer_id) references fec_committees (committee_id);

