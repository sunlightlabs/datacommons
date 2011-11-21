
drop table if exists fec_candidates;
create table fec_candidates as
select *,
    case
        when substring(candidate_id for 1) = 'P' then 'P'
        when substring(candidate_id for 1) = 'S' then 'S' || '-' || substring(candidate_id from 3 for 2)
        when substring(candidate_id for 1) = 'H' then 'H' || '-' || substring(candidate_id from 3 for 2) || '-' || current_district
    end as race
from fec_candidates_import;

-- alter table fec_candidate_summaries alter column ending_date type date using (substring(ending_date from 5 for 4) || substring(ending_date from 1 for 2) || substring(ending_date from 3 for 2))::date; 


drop table if exists fec_indiv;
create table fec_indiv as
select fec_record, filer_id, transaction_type, contributor_lender_transfer as contributor_name, state, occupation, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount
from fec_indiv_import;

drop table if exists fec_pac2cand;
create table fec_pac2cand as
select fec_record, filer_id, transaction_type, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id, candidate_id
from fec_pac2cand_import;

drop table if exists fec_pac2pac;
create table fec_pac2pac as
select fec_record, filer_id, transaction_type, contributor_lender_transfer as contributor_name, state, occupation, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id
from fec_pac2pac_import;   


-- these three are unfortunately not true in the data
-- alter table fec_candidates add constraint fec_candidates_committee_id foreign key (committee_id) references fec_committees (committee_id);
-- alter table fec_committees add constraint fec_committees_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);
-- alter table fec_pac2cand add constraint fec_pac2cand_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);

-- constraints are making the loading process more difficult...
-- and not sure they give us any real benefit, so considering removing them.
-- alter table fec_indiv add constraint fec_indiv_filer_id foreign key (filer_id) references fec_committees (committee_id);
-- alter table fec_pac2cand add constraint fec_pac2cand_filer_id foreign key (filer_id) references fec_committees (committee_id);
-- alter table fec_pac2pac add constraint fec_pac2pac_filer_id foreign key (filer_id) references fec_committees (committee_id);



