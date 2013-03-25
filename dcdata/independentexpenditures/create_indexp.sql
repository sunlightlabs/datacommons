drop table if exists fec_indexp_import;
create table fec_indexp_import (
    candidate_id varchar(9),
    candidate_name varchar,
    spender_id varchar(9),
    spender_name varchar,
    election_type varchar(5),
    candidate_state varchar(2),
    candidate_district varchar(2),
    candidate_office varchar(9),
    candidate_party varchar(32),
    amount varchar(15),
    date date,
    aggregate_amount varchar(15),
    support_oppose varchar(9),
    purpose varchar(100),
    payee varchar(90),
    filing_number varchar(6),
    amendment varchar(2),
    transaction_id varchar(32),
    image_number varchar(11),
    received_date date,
    prev_file_num varchar(6),
    cycle smallint
);

drop table if exists fec_indexp cascade;
CREATE TABLE fec_indexp (
    cycle smallint,
    candidate_id character varying(9),
    candidate_name character varying,
    spender_id character varying(9),
    spender_name character varying,
    election_type character varying(5),
    candidate_state character varying(2),
    candidate_district character varying,
    candidate_office character varying(9),
    candidate_party character varying(32),
    amount numeric,
    aggregate_amount numeric,
    support_oppose character varying(9),
    date date,
    purpose character varying(100),
    payee character varying(90),
    filing_number character varying(6),
    amendment character varying(2),
    transaction_id character varying(32),
    image_number character varying(11),
    received_date date
);
-- just here to trigger errors if something is wrong with the data
alter table fec_indexp add constraint fec_indexp_transactions unique (spender_id, filing_number, transaction_id);

drop table if exists fec_indexp_out_of_date_cycles;
create table fec_indexp_out_of_date_cycles (cycle smallint);

drop table if exists agg_fec_indexp;
CREATE TABLE agg_fec_indexp (
    cycle smallint,
    candidate_entity uuid,
    candidate_name character varying,
    committee_entity uuid,
    committee_name character varying,
    support_oppose character varying(9),
    amount numeric
);
create index agg_fec_indexp__candidate_entity on agg_fec_indexp (candidate_entity);
create index agg_fec_indexp__committee_entity on agg_fec_indexp (committee_entity);
create index agg_fec_indexp__cycle on agg_fec_indexp (cycle);

drop table agg_fec_indexp_totals;
CREATE TABLE agg_fec_indexp_totals (
    cycle smallint,
    entity_id uuid,
    spending_amount numeric
);
create index agg_fec_indexp_totals__entity_id on agg_fec_indexp_totals (entity_id);
create index agg_fec_indexp_totals__cycle on agg_fec_indexp_totals (cycle);



