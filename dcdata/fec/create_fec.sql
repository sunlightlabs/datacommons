-- BEGIN: SOURCE TABLES
drop table if exists fec_candidates cascade;
create table fec_candidates (
    candidate_id varchar(9),
    cycle smallint,
    candidate_name varchar(200),
    party varchar(3),
    election_year integer,
    race varchar(7),
    office_state varchar(2),
    office varchar(1),
    office_district varchar(2),
    incumbent_challenger_open varchar(1),
    candidate_status varchar(1),
    committee_id varchar(9),
    street1 varchar(34),
    street2 varchar(34),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    primary key (candidate_id, cycle)
);

drop table if exists fec_committees cascade;
create table fec_committees (
    committee_id varchar(9),
    cycle smallint,
    committee_name varchar(200),
    treasurers_name varchar(90),
    street1 varchar(34),
    street2 varchar(34),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    committee_designation varchar(1),
    committee_type varchar(1),
    committee_party varchar(3),
    filing_frequency varchar(1),
    interest_group varchar(1),
    connected_org varchar(200),
    candidate_id varchar(9),
    primary key (committee_id, cycle)
);

drop table if exists fec_indiv cascade;
create table fec_indiv (
    cycle smallint,
    filer_id varchar(9),
    amendment varchar(1),
    report_type varchar(3),
    election_type varchar(5),
    microfilm_location varchar(11),
    transaction_type varchar(3),
    entity_type varchar(3),
    contributor_name varchar(200),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    employer varchar(38),
    occupation varchar(38),
    "date" date,
    amount numeric(14,2),
    other_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);
create index fec_indiv__cycle on fec_indiv (cycle);
create index fec_indiv__filer_id on fec_indiv (filer_id);

drop table if exists fec_pac2cand cascade;
create table fec_pac2cand (
    cycle smallint,
    filer_id varchar(9),
    amendment varchar(1),
    report_type varchar(3),
    election_type varchar(5),
    microfilm_location varchar(11),
    transaction_type varchar(3),
    entity_type varchar(3),
    contributor_name varchar(200),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    employer varchar(38),
    occupation varchar(38),
    "date" date,
    amount numeric(14,2),
    other_id varchar(9),
    candidate_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);
create index fec_pac2cand__cycle on fec_pac2cand (cycle);
create index fec_pac2cand__filer_id on fec_pac2cand (filer_id);

drop table if exists fec_pac2pac cascade;
CREATE TABLE fec_pac2pac (
    cycle smallint,
    filer_id varchar(9),
    amendment varchar(1),
    report_type varchar(3),
    election_type varchar(5),
    microfilm_location varchar(11),
    transaction_type varchar(3),
    entity_type varchar(3),
    contributor_name varchar(200),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    employer varchar(38),
    occupation varchar(38),
    "date" date,
    amount numeric(14,2),
    other_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);
create index fec_pac2pac__cycle on fec_pac2pac (cycle);
create index fec_pac2pac__filer_id on fec_pac2pac (filer_id);

drop table if exists fec_candidate_summaries cascade;
CREATE TABLE fec_candidate_summaries (
    candidate_id varchar(9),
    cycle smallint,
    candidate_name varchar(200),
    incumbent_challenger_open varchar(1),
    party varchar(1),
    party_affiliation varchar(3),
    total_receipts numeric(14,2),                            -- 22
    authorized_transfers_from numeric(14,2),                 -- 18
    total_disbursements numeric(14,2),                       -- 30
    transfers_to_authorized numeric(14,2),                   -- 24
    beginning_cash numeric(14,2),                            -- 6
    ending_cash numeric(14,2),                               -- 10
    contributions_from_candidate numeric(14,2),              -- 17d
    loans_from_candidate numeric(14,2),                      -- 19a
    other_loans numeric(14,2),                               -- 19b
    candidate_loan_repayments numeric(14,2),                 -- 27a
    other_loan_repayments numeric(14,2),                     -- 27b
    debts_owed_by numeric(14,2),                             -- 12
    total_individual_contributions numeric(14,2),            -- 17a
    state varchar(2),
    district varchar(2),
    special_election_status varchar(1),
    primary_election_status varchar(1),
    runoff_election_status varchar(1),
    general_election_status varchar(1),
    general_election_ct numeric(7,4),
    contributions_from_other_committees numeric(14,2),       -- 17c
    contributions_from_party_committees numeric(14,2),       -- 17b
    ending_date date,
    refunds_to_individuals numeric(14,2),                    -- 28a
    refunds_to_committees numeric(14,2),                     -- 28b & 28c?
    primary key (candidate_id, cycle)
);

drop table if exists fec_committee_summaries cascade;
CREATE TABLE fec_committee_summaries (
    committee_id varchar(9),
    cycle smallint,
    committee_name varchar(200),
    committee_type varchar(1),
    committee_designation varchar(1),
    filing_frequency varchar(1),
    total_receipts numeric(14,2),
    transfers_from_affiliates numeric(14,2),
    individual_contributions numeric(14,2),
    contributions_from_other_committees numeric(14,2),
    contributions_from_candidate numeric(14,2),
    candidate_loans numeric(14,2),
    total_loans_received numeric(14,2),
    total_disbursements numeric(14,2),
    transfers_to_affiliates numeric(14,2),
    refunds_to_individuals numeric(14,2),
    refunds_to_committees numeric(14,2),
    candidate_loan_repayments numeric(14,2),
    loan_repayments numeric(14,2),
    cash_beginning_of_year numeric(14,2),
    cash_close_of_period numeric(14,2),
    debts_owed numeric(14,2),
    nonfederal_transfers_received numeric(14,2),
    contributions_to_committees numeric(14,2),
    independent_expenditures_made numeric(14,2),
    party_coordinated_expenditures_made numeric(14,2),
    nonfederal_expenditure_share numeric(14,2),
    through_date date,
    primary key (committee_id, cycle)
);

-- END: SOURCE TABLES

-- BEGIN: UTILITY TABLES

drop table if exists fec_out_of_date_cycles cascade;
create table fec_out_of_date_cycles (
    cycle smallint not null,
    created_at timestamp default(now())
);

drop table if exists fec_cycles cascade;
create table fec_cycles (
    cycle smallint not null,
    created_at timestamp default(now())
);

-- END: UTILITY TABLES

-- BEGIN: AGGREGATE/COMPUTED TABLES

CREATE TABLE agg_fec_candidate_cumulative_timeline (
    candidate_id character varying(9),
    cycle smallint,
    race text,
    week integer,
    cumulative_raised numeric
);
CREATE TABLE agg_fec_candidate_rankings (
    candidate_id character varying(9),
    office character varying(1),
    election_year integer,
    primary_election_status character varying,
    num_candidates_in_field bigint,
    total_receipts_rank bigint,
    cash_on_hand_rank bigint,
    total_disbursements_rank bigint
);
CREATE TABLE agg_fec_candidate_timeline (
    candidate_id character varying(9),
    cycle smallint,
    race text,
    week integer,
    count bigint,
    amount numeric
);
CREATE TABLE agg_fec_committee_summaries (
    cycle integer,
    entity_id uuid,
    total_raised numeric,
    individual_contributions numeric,
    contributions_from_other_committees numeric,
    transfers_from_affiliates numeric,
    nonfederal_transfers_received numeric,
    total_loans_received numeric,
    total_disbursements numeric,
    cash_close_of_period numeric,
    debts_owed numeric,
    contributions_to_committees numeric,
    independent_expenditures_made numeric,
    party_coordinated_expenditures_made numeric,
    nonfederal_expenditure_share numeric,
    min_through_date date,
    max_through_date date,
    count bigint
);
create index agg_fec_committee_summaries__cycle on agg_fec_committee_summaries (cycle);
create index agg_fec_committee_summaries__entity_id on agg_fec_committee_summaries (entity_id);

CREATE TABLE agg_fec_race_status (
    election_year integer,
    race text,
    special_election_status text,
    primary_election_status text,
    runoff_election_status text,
    general_election_status text
);

CREATE TABLE fec_candidate_itemized (
    contributor_name character varying(200),
    cycle smallint,
    date date,
    amount numeric,
    contributor_type text,
    transaction_type text,
    employer character varying,
    occupation character varying,
    city character varying(30),
    state character varying(2),
    zipcode character varying(9),
    candidate_name character varying(200),
    party character varying(3),
    race text,
    status character varying(1),
    committee_id character varying(9),
    candidate_id character varying(9)
);
create index fec_candidate_itemized_candidate_id on fec_candidate_itemized (candidate_id);
create index fec_candidate_itemized_committee_id on fec_candidate_itemized (committee_id);
create index fec_candidate_itemized_cycle on fec_candidate_itemized (cycle);
create index fec_candidate_itemized_date on fec_candidate_itemized (date);
create index fec_candidate_itemized__transaction_type_idx on fec_candidate_itemized (transaction_type);

CREATE TABLE fec_committee_itemized (
    contributor_name character varying(200),
    cycle smallint,
    date date,
    amount numeric,
    contributor_type text,
    contributor_committee_id character varying,
    transaction_type text,
    employer character varying,
    occupation character varying(38),
    city character varying(30),
    state character varying(2),
    zipcode character varying(9),
    committee_name character varying(200),
    committee_id character varying(9),
    committee_designation character varying(1),
    committee_type character varying(1),
    committee_party character varying(3),
    interest_group character varying(1),
    connected_org character varying(200),
    candidate_id character varying(9)
);
create index fec_committee_itemized__cycle on fec_committee_itemized (cycle);
create index fec_candidate_itemized_date on fec_candidate_itemized (date);
create index fec_committee_itemized__committee_id on fec_committee_itemized (committee_id);
create index fec_committee_itemized__transaction_type_idx on fec_committee_itemized (transaction_type);

-- END: AGGREGATE/COMPUTED TABLES
