
drop table if exists fec_indiv;
create table fec_indiv as
select filer_id, transaction_type, contributor_lender_transfer as contributor_name, state, occupation, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount
from fec_indiv_import; 

drop table if exists fec_pac2cand;
create table fec_pac2cand as
select filer_id, transaction_type, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id, candidate_id, fec_record
from fec_pac2cand_import;

drop table if exists fec_pac2pac;
create table fec_pac2pac as
select filer_id, transaction_type, contributor_lender_transfer as contributor_name, state, occupation, 
    (transaction_century || transaction_year || transaction_month || transaction_day)::date as date,
    overpunch(amount) as amount,
    other_id, fec_record
from fec_pac2pac_import;   


-- these three are unfortunately not true in the data
-- alter table fec_candidates add constraint fec_candidates_committee_id foreign key (committee_id) references fec_committees (committee_id);
-- alter table fec_committees add constraint fec_committees_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);
-- alter table fec_pac2cand add constraint fec_pac2cand_candidate_id foreign key (candidate_id) references fec_candidates (candidate_id);

alter table fec_indiv add constraint fec_indiv_filer_id foreign key (filer_id) references fec_committees (committee_id);
alter table fec_pac2cand add constraint fec_pac2cand_filer_id foreign key (filer_id) references fec_committees (committee_id);
alter table fec_pac2pac add constraint fec_pac2pac_filer_id foreign key (filer_id) references fec_committees (committee_id);



