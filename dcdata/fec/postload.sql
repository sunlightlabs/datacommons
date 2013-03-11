insert into fec_candidates (
    candidate_id, cycle, candidate_name, party, election_year, race,
    office_state, office, office_district, incumbent_challenger_open, 
    candidate_status, committee_id, street1, street2, city, state, zipcode
)
select 
    candidate_id,
    to_cycle(election_year) as cycle, 
    candidate_name,
    party,
    election_year,
    case
        when office = 'P' then 'P'
        when office = 'S' then 'S' || '-' || office_state
        when office = 'H' then 'H' || '-' || office_state || '-' || office_district
    end as race,
    office_state,
    office,
    office_district,
    incumbent_challenger_open,
    candidate_status,
    committee_id,
    street1,
    street2,
    city,
    state,
    zipcode
from tmp_fec_candidates;


insert into fec_committees (
    committee_id,
    cycle,
    committee_name,
    treasurers_name,
    street1,
    street2,
    city,
    state,
    zipcode,
    committee_designation,
    committee_type,
    committee_party,
    filing_frequency,
    interest_group,
    connected_org,
    candidate_id
) select
    committee_id,
    cycle,
    committee_name,
    treasurers_name,
    street1,
    street2,
    city,
    state,
    zipcode,
    committee_designation,
    committee_type,
    committee_party,
    filing_frequency,
    interest_group,
    connected_org,
    candidate_id
from tmp_fec_committees;


insert into fec_indiv (
    cycle, filer_id, amendment, report_type, election_type, microfilm_location, 
    transaction_type, entity_type, contributor_name, city, state, zipcode,
    employer, occupation, date, amount, other_id, transaction_id, file_num,
    memo_code, memo_text, fec_record
)
select
    to_cycle(to_date(date, 'MMDDYYYY')) as cycle,
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
    to_date(date, 'MMDDYYYY') as date,
    case when transaction_type = '22Y' then -abs(amount) else amount end as amount,
    other_id,
    transaction_id,
    file_num,
    memo_code,
    memo_text,
    fec_record
from tmp_fec_indiv
where date is not null and to_date(date, 'MMDDYYYY') < '20210101'::date
;

insert into fec_pac2cand (
    cycle, filer_id, amendment, report_type, election_type, microfilm_location,
    transaction_type, entity_type, contributor_name, city, state, zipcode,
    employer, occupation, date, amount, other_id, candidate_id, transaction_id,
    file_num, memo_code, memo_text, fec_record
)
select
    to_cycle(to_date(date, 'MMDDYYYY')) as cycle,
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
    to_date(date, 'MMDDYYYY') as date,
    case when transaction_type = '22Z' then -abs(amount) else amount end as amount,
    other_id,
    candidate_id,
    transaction_id,
    file_num,
    memo_code,
    memo_text,
    fec_record
from tmp_fec_pac2cand
where date is not null and to_date(date, 'MMDDYYYY') < '20210101'::date
;

insert into fec_pac2pac (
    cycle, filer_id, amendment, report_type, election_type, microfilm_location,
    transaction_type, entity_type, contributor_name, city, state, zipcode,
    employer, occupation, date, amount, other_id, transaction_id, file_num,
    memo_code, memo_text, fec_record
)
select
    to_cycle(to_date(date, 'MMDDYYYY')) as cycle,
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
    to_date(date, 'MMDDYYYY') as date,
    case when transaction_type = '22Z' then -abs(amount) else amount end as amount,
    other_id,
    transaction_id,
    file_num,
    memo_code,
    memo_text,
    fec_record
from tmp_fec_pac2pac
where date is not null and to_date(date, 'MMDDYYYY') < '20210101'::date
;

insert into fec_candidate_summaries (
    candidate_id, cycle, candidate_name, incumbent_challenger_open,
    party, party_affiliation, total_receipts, authorized_transfers_from,
    total_disbursements, transfers_to_authorized, beginning_cash, ending_cash,
    contributions_from_candidate, loans_from_candidate, other_loans,
    candidate_loan_repayments, other_loan_repayments, debts_owed_by,
    total_individual_contributions, state, district, special_election_status,
    primary_election_status, runoff_election_status, general_election_status,
    general_election_ct, contributions_from_other_committees,
    contributions_from_party_committees, ending_date, refunds_to_individuals,
    refunds_to_committees
)
select
    candidate_id,
    to_cycle(ending_date) as cycle,
    candidate_name,
    incumbent_challenger_open,
    party,
    party_affiliation,
    total_receipts,
    authorized_transfers_from,
    total_disbursements,
    transfers_to_authorized,
    beginning_cash,
    ending_cash,
    contributions_from_candidate,
    loans_from_candidate,
    other_loans,
    candidate_loan_repayments,
    other_loan_repayments,
    debts_owed_by,
    total_individual_contributions,
    state,
    district,
    special_election_status,
    primary_election_status,
    runoff_election_status,
    general_election_status,
    general_election_ct,
    contributions_from_other_committees,
    contributions_from_party_committees,
    ending_date,
    refunds_to_individuals,
    refunds_to_committees
from tmp_fec_candidate_summaries
where ending_date is not null and ending_date < '20210101'::date
;

insert into fec_committee_summaries (
    committee_id, cycle, committee_name, committee_type,
    committee_designation, filing_frequency, total_receipts, 
    transfers_from_affiliates, individual_contributions, 
    contributions_from_other_committees, contributions_from_candidate, 
    candidate_loans, total_loans_received, total_disbursements, 
    transfers_to_affiliates, refunds_to_individuals, refunds_to_committees, 
    candidate_loan_repayments, loan_repayments, cash_beginning_of_year, 
    cash_close_of_period, debts_owed, nonfederal_transfers_received, 
    contributions_to_committees, independent_expenditures_made, 
    party_coordinated_expenditures_made, nonfederal_expenditure_share, 
    through_date
)
select
    committee_id,
    cycle,
    committee_name,
    committee_type,
    committee_designation,
    filing_frequency,
    total_receipts,
    transfers_from_affiliates,
    individual_contributions,
    contributions_from_other_committees,
    contributions_from_candidate,
    candidate_loans,
    total_loans_received,
    total_disbursements,
    transfers_to_affiliates,
    refunds_to_individuals,
    refunds_to_committees,
    candidate_loan_repayments,
    loan_repayments,
    cash_beginning_of_year,
    cash_close_of_period,
    debts_owed,
    nonfederal_transfers_received,
    contributions_to_committees,
    independent_expenditures_made,
    party_coordinated_expenditures_made,
    nonfederal_expenditure_share,
    through_date
from tmp_fec_committee_summaries
where through_date is not null and through_date < '20210101'::date
;


-- END POSTPROCESSING
-- BEGIN AGGREGATES

delete from agg_fec_race_status where to_cycle(election_year) in (select cycle from fec_out_of_date_cycles);
insert into agg_fec_race_status
select
    election_year,
    race,
    max(special_election_status) as special_election_status,
    max(primary_election_status) as primary_election_status,
    max(runoff_election_status) as runoff_election_status,
    max(general_election_status) as general_election_status
from fec_candidate_summaries s 
    inner join fec_out_of_date_cycles using (cycle)
    inner join fec_candidates c using (candidate_id, cycle) 
where candidate_status = 'C' 
group by election_year, race;


delete from agg_fec_candidate_rankings where to_cycle(election_year) in (select cycle from fec_out_of_date_cycles);
insert into agg_fec_candidate_rankings

-- primary winners only (vs. primary winners)
with counts_by_office_primary_year as (
    -- count of general election candidates
    select count(*) as num_candidates_in_field, office, 'W' as primary_election_status, election_year
    from fec_candidates c
        inner join fec_out_of_date_cycles using (cycle)
        inner join fec_candidate_summaries s using (candidate_id)
    where candidate_status = 'C' and s.primary_election_status = 'W'
    group by office, election_year

    union all

    -- count of primary field
    select count(*) as num_candidates_in_field, office, null as primary_election_status, election_year
    from fec_candidates c
        inner join fec_out_of_date_cycles using (cycle)
        inner join fec_candidate_summaries s using (candidate_id)
    where candidate_status = 'C'
    group by office, election_year
)
-- general election rankings
select candidate_id, office, election_year, primary_election_status, num_candidates_in_field,
    rank() over (partition by office, election_year order by total_receipts desc) as total_receipts_rank,
    rank() over (partition by office, election_year order by ending_cash desc) as cash_on_hand_rank,
    rank() over (partition by office, election_year order by total_disbursements desc) as total_disbursements_rank
from fec_candidates c
    inner join fec_candidate_summaries s using (candidate_id, cycle)
    inner join counts_by_office_primary_year ct using (office, election_year, primary_election_status)
where
    candidate_status = 'C'
    and s.primary_election_status = 'W'

union all

-- primary candidates (vs. everybody)
select candidate_id, x.office, x.election_year, x.primary_election_status, num_candidates_in_field, total_receipts_rank, cash_on_hand_rank, total_disbursements_rank
from (
    select candidate_id, office, election_year, s.primary_election_status,
        rank() over (partition by office, election_year order by total_receipts desc) as total_receipts_rank,
        rank() over (partition by office, election_year order by ending_cash desc) as cash_on_hand_rank,
        rank() over (partition by office, election_year order by total_disbursements desc) as total_disbursements_rank
    from fec_candidates c
        inner join fec_out_of_date_cycles using (cycle)
        inner join fec_candidate_summaries s using (candidate_id)
    where candidate_status = 'C'
)x
inner join counts_by_office_primary_year ct
    on x.office = ct.office
    and x.election_year = ct.election_year
where x.primary_election_status is null
;

delete from agg_fec_candidate_timeline where cycle in (select cycle from fec_out_of_date_cycles);
insert into agg_fec_candidate_timeline
select
    candidate_id, 
    c.cycle,
    race, 
    (date - ((to_cycle(date) - 1)::text || '-01-01')::date) / 7 as week,
    count(*),
    sum(amount) as amount
from fec_candidates c
    inner join fec_out_of_date_cycles using (cycle)
    inner join fec_candidate_summaries s using (candidate_id, cycle)
    inner join (
        select filer_id, cycle, date, amount from fec_indiv 
        union all 
        select other_id, cycle, date, amount from fec_pac2cand
    ) t on c.committee_id = t.filer_id and c.cycle = t.cycle
group by 
    candidate_id, c.cycle, race, week;

delete from agg_fec_candidate_cumulative_timeline where cycle in (select cycle from fec_out_of_date_cycles);
insert into agg_fec_candidate_cumulative_timeline
select 
    candidate_id, 
    cycle,
    race, 
    week, 
    sum(amount) OVER (partition by candidate_id, cycle, race order by week) as cumulative_raised
from agg_fec_candidate_timeline
    inner join fec_out_of_date_cycles using (cycle)
;


delete from fec_candidate_itemized where cycle in (select cycle from fec_out_of_date_cycles);
insert into fec_candidate_itemized
select
    contributor_name, cycle, date, amount,
    contributor_type, transaction_type, employer, occupation,
    i.city, i.state, i.zipcode, candidate_name,
    party, race, incumbent_challenger_open as status, committee_id,
    candidate_id
from fec_candidates c
    inner join fec_out_of_date_cycles using (cycle)
    inner join (
        select filer_id as committee_id, 'indiv' as contributor_type, contributor_name,
            i.city, i.state, i.zipcode, employer, occupation,
            date, amount, transaction_type, cycle
        from fec_indiv i

        union all

        select other_id, 'pac', committee_name,
            t.city, t.state, t.zipcode, connected_org, '',
            date, amount, transaction_type, t.cycle
        from fec_pac2cand t
        inner join fec_committees c on c.committee_id = t.filer_id and c.cycle = t.cycle
    ) i using (committee_id, cycle)
;


delete from fec_committee_itemized where cycle in (select cycle from fec_out_of_date_cycles);
insert into fec_committee_itemized
select
    contributor_name, cycle, date, amount, contributor_type,
    contributor_committee_id, transaction_type, employer, occupation,
    i.city, i.state, i.zipcode, committee_name,
    committee_id, committee_designation, committee_type, committee_party,
    interest_group, connected_org, candidate_id
from fec_committees c
    inner join fec_out_of_date_cycles using (cycle)
    inner join (
        select
            filer_id as committee_id,
            'indiv' as contributor_type,
            contributor_name,
            '' as contributor_committee_id,
            city,
            state,
            zipcode,
            employer,
            occupation,
            date,
            amount,
            transaction_type,
            cycle
        from fec_indiv

        union all

        select 
            filer_id as committee_id,
            'pac' as contributor_type,
            contributor_name,
            other_id as contributor_committee_id,
            city,
            state,
            zipcode,
            '' as employer,
            occupation,
            date,
            amount,
            transaction_type,
            cycle
        from fec_pac2pac
    ) i using (committee_id, cycle)
    where
        -- only transaction types 10-19 are money coming in. 20-29 are money going out, 
        -- which we're not interested in here.
        substring(transaction_type for 2)::integer between 10 and 19
;


delete from agg_fec_committee_summaries where cycle in (select cycle from fec_out_of_date_cycles);
insert into agg_fec_committee_summaries
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
    inner join fec_out_of_date_cycles using (cycle)
    inner join matchbox_entityattribute a 
        on c.committee_id = a.value 
        and a.namespace = 'urn:fec:committee'
--cross join (values (-1), (2014)) as cycles (cycle)
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

