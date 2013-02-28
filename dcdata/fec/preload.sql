create temp table tmp_fec_candidates as (select * from fec_candidates limit 0);
create temp table tmp_fec_committees as (select * from fec_committees limit 0);
create temp table tmp_fec_indiv as (select * from fec_indiv limit 0);
create temp table tmp_fec_pac2cand as (select * from fec_pac2cand limit 0);
create temp table tmp_fec_pac2pac as (select * from fec_pac2pac limit 0);
create temp table tmp_fec_candidate_summaries as (select * from fec_candidate_summaries limit 0);
create temp table tmp_fec_committee_summaries as (select * from fec_committee_summaries limit 0);

alter table tmp_fec_candidates drop column cycle;
alter table tmp_fec_candidates drop column race;
alter table tmp_fec_committees drop column cycle;
alter table tmp_fec_indiv drop column cycle;
alter table tmp_fec_pac2cand drop column cycle;
alter table tmp_fec_pac2pac drop column cycle;
alter table tmp_fec_candidate_summaries drop column cycle;
alter table tmp_fec_committee_summaries drop column cycle;

alter table tmp_fec_indiv alter column "date" type varchar(8);
alter table tmp_fec_pac2cand alter column "date" type varchar(8);
alter table tmp_fec_pac2pac alter column "date" type varchar(8);
