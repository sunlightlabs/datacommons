
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
    select 2000, * from fec_candidates_00
union all
    select 1998, * from fec_candidates_98
union all
    select 1996, * from fec_candidates_96;

drop table if exists fec_candidates_allcycles;
create table fec_candidates_allcycles as
select *,
    case
        when office = 'P' then 'P'
        when office = 'S' then 'S' || '-' || office_state
        when office = 'H' then 'H' || '-' || office_state || '-' || office_district
    end as race
from fec_candidates_allcycles_import;

create index fec_candidates_allcycles_candidate_id on fec_candidates_allcycles (candidate_id);


create table fec_committees_allcycles as
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
    select 2000, * from fec_committees_00
union all
    select 1998, * from fec_committees_98
union all
    select 1996, * from fec_committees_96;

create index fec_committees_allcycles_committee_id on fec_committees_allcycles (committee_id);


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
    select 2000, * from fec_indiv_00
union all
    select 1998, * from fec_indiv_98
union all
    select 1996, * from fec_indiv_96;

drop table if exists fec_indiv_allcycles;
create table fec_indiv_allcycles as
    select
        cycle,
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
    select 2000, * from fec_pac2cand_00
union all
    select 1998, * from fec_pac2cand_98
union all
    select 1996, * from fec_pac2cand_96;

drop table if exists fec_pac2cand_allcycles;
create table fec_pac2cand_allcycles as
    select
        cycle,
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
        candidate_id,
        transaction_id,
        file_num,
        memo_code,
        memo_text,
        fec_record
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
    select 2000, * from fec_pac2pac_00
union all
    select 1998, * from fec_pac2pac_98
union all
    select 1996, * from fec_pac2pac_96;

drop table if exists fec_pac2pac_allcycles;
create table fec_pac2pac_allcycles as
select
    cycle,
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
from fec_pac2pac_allcycles_import;

create index fec_pac2pac_allcycles_filer_id on fec_pac2pac_allcycles (filer_id);
create index fec_pac2pac_allcycles_other_id on fec_pac2pac_allcycles (other_id);


create table fec_committee_summaries_allcycles as
    select 2012 as cycle, * from fec_committee_summaries_12
    union all
    select 2010, * from fec_committee_summaries_10
    union all 
    select 2008, * from fec_committee_summaries_08
    union all 
    select 2006, * from fec_committee_summaries_06
    union all 
    select 2004, * from fec_committee_summaries_04
    union all 
    select 2002, * from fec_committee_summaries_02
    union all 
    select 2000, * from fec_committee_summaries_00
    union all 
    select 1998, * from fec_committee_summaries_98
    union all 
    select 1996, * from fec_committee_summaries_96;
    
create index fec_committee_summaries_allcycles_committee_id on fec_committee_summaries_allcycles (committee_id);


create table fec_candidate_summaries_allcycles as
    select 2012 as cycle, * from fec_candidate_summaries_12
    union all
    select 2010, * from fec_candidate_summaries_10
    union all 
    select 2008, * from fec_candidate_summaries_08
    union all 
    select 2006, * from fec_candidate_summaries_06
    union all 
    select 2004, * from fec_candidate_summaries_04
    union all 
    select 2002, * from fec_candidate_summaries_02
    union all 
    select 2000, * from fec_candidate_summaries_00
    union all 
    select 1998, * from fec_candidate_summaries_98
    union all 
    select 1996, * from fec_candidate_summaries_96;

create index fec_candidates_allcycles_committee_id on fec_candidates_allcycles (committee_id);
