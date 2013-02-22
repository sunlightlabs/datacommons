drop table if exists fec_candidate_summaries_12 cascade;
drop table if exists fec_candidate_summaries_10 cascade;
drop table if exists fec_candidate_summaries_08 cascade;
drop table if exists fec_candidate_summaries_06 cascade;
drop table if exists fec_candidate_summaries_04 cascade;
drop table if exists fec_candidate_summaries_02 cascade;
drop table if exists fec_candidate_summaries_00 cascade;
drop table if exists fec_candidate_summaries_98 cascade;
drop table if exists fec_candidate_summaries_96 cascade;


drop table if exists fec_committee_summaries_12 cascade;
drop table if exists fec_committee_summaries_10 cascade;
drop table if exists fec_committee_summaries_08 cascade;
drop table if exists fec_committee_summaries_06 cascade;
drop table if exists fec_committee_summaries_04 cascade;
drop table if exists fec_committee_summaries_02 cascade;
drop table if exists fec_committee_summaries_00 cascade;
drop table if exists fec_committee_summaries_98 cascade;
drop table if exists fec_committee_summaries_96 cascade;

drop table if exists fec_candidates_96 cascade;
drop table if exists fec_candidates_98 cascade;
drop table if exists fec_candidates_00 cascade;
drop table if exists fec_candidates_02 cascade;
drop table if exists fec_candidates_04 cascade;
drop table if exists fec_candidates_06 cascade;
drop table if exists fec_candidates_08 cascade;
drop table if exists fec_candidates_10 cascade;
drop table if exists fec_candidates_12 cascade;

    
drop table if exists fec_committees_96 cascade;
drop table if exists fec_committees_98 cascade;
drop table if exists fec_committees_00 cascade;
drop table if exists fec_committees_02 cascade;
drop table if exists fec_committees_04 cascade;
drop table if exists fec_committees_06 cascade;
drop table if exists fec_committees_08 cascade;
drop table if exists fec_committees_10 cascade;
drop table if exists fec_committees_12 cascade;

    
drop table if exists fec_indiv_96 cascade;
drop table if exists fec_indiv_98 cascade;
drop table if exists fec_indiv_00 cascade;
drop table if exists fec_indiv_02 cascade;
drop table if exists fec_indiv_04 cascade;
drop table if exists fec_indiv_06 cascade;
drop table if exists fec_indiv_08 cascade;
drop table if exists fec_indiv_10 cascade;
drop table if exists fec_indiv_12 cascade;

    
drop table if exists fec_pac2cand_96 cascade;
drop table if exists fec_pac2cand_98 cascade;
drop table if exists fec_pac2cand_00 cascade;
drop table if exists fec_pac2cand_02 cascade;
drop table if exists fec_pac2cand_04 cascade;
drop table if exists fec_pac2cand_06 cascade;
drop table if exists fec_pac2cand_08 cascade;
drop table if exists fec_pac2cand_10 cascade;
drop table if exists fec_pac2cand_12 cascade;

    
drop table if exists fec_pac2pac_96 cascade;
drop table if exists fec_pac2pac_98 cascade;
drop table if exists fec_pac2pac_00 cascade;
drop table if exists fec_pac2pac_02 cascade;
drop table if exists fec_pac2pac_04 cascade;
drop table if exists fec_pac2pac_06 cascade;
drop table if exists fec_pac2pac_08 cascade;
drop table if exists fec_pac2pac_10 cascade;
drop table if exists fec_pac2pac_12 cascade;



create table fec_candidate_summaries_12 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_10 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_08 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_06 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_04 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_02 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_00 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_98 as select * from fec_candidate_summaries limit 0;
create table fec_candidate_summaries_96 as select * from fec_candidate_summaries limit 0;


create table fec_committee_summaries_12 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_10 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_08 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_06 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_04 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_02 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_00 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_98 as select * from fec_committee_summaries limit 0;
create table fec_committee_summaries_96 as select * from fec_committee_summaries limit 0;

create table fec_candidates_96 as select * from fec_candidates_import limit 0;
create table fec_candidates_98 as select * from fec_candidates_import limit 0;
create table fec_candidates_00 as select * from fec_candidates_import limit 0;
create table fec_candidates_02 as select * from fec_candidates_import limit 0;
create table fec_candidates_04 as select * from fec_candidates_import limit 0;
create table fec_candidates_06 as select * from fec_candidates_import limit 0;
create table fec_candidates_08 as select * from fec_candidates_import limit 0;
create table fec_candidates_10 as select * from fec_candidates_import limit 0;
create table fec_candidates_12 as select * from fec_candidates_import limit 0;

    
create table fec_committees_96 as select * from fec_committees limit 0;
create table fec_committees_98 as select * from fec_committees limit 0;
create table fec_committees_00 as select * from fec_committees limit 0;
create table fec_committees_02 as select * from fec_committees limit 0;
create table fec_committees_04 as select * from fec_committees limit 0;
create table fec_committees_06 as select * from fec_committees limit 0;
create table fec_committees_08 as select * from fec_committees limit 0;
create table fec_committees_10 as select * from fec_committees limit 0;
create table fec_committees_12 as select * from fec_committees limit 0;

    
create table fec_indiv_96 as select * from fec_indiv_import limit 0;
create table fec_indiv_98 as select * from fec_indiv_import limit 0;
create table fec_indiv_00 as select * from fec_indiv_import limit 0;
create table fec_indiv_02 as select * from fec_indiv_import limit 0;
create table fec_indiv_04 as select * from fec_indiv_import limit 0;
create table fec_indiv_06 as select * from fec_indiv_import limit 0;
create table fec_indiv_08 as select * from fec_indiv_import limit 0;
create table fec_indiv_10 as select * from fec_indiv_import limit 0;
create table fec_indiv_12 as select * from fec_indiv_import limit 0;

    
create table fec_pac2cand_96 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_98 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_00 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_02 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_04 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_06 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_08 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_10 as select * from fec_pac2cand_import limit 0;
create table fec_pac2cand_12 as select * from fec_pac2cand_import limit 0;

    
create table fec_pac2pac_96 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_98 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_00 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_02 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_04 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_06 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_08 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_10 as select * from fec_pac2pac_import limit 0;
create table fec_pac2pac_12 as select * from fec_pac2pac_import limit 0;
