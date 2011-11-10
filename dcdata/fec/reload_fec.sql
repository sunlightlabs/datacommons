
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
    other_id, candidate_id, fec_record
from fec_pac2cand_import;   
