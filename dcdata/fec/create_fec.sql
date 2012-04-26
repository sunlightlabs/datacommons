
drop table if exists fec_candidates_import;
create table fec_candidates_import (
    candidate_id varchar(9),
    candidate_name varchar(38),
    party_designation1 varchar(3),
    filler1 varchar(3),
    party_designation3 varchar(3),
    incumbent_challenger_open varchar(1),
    filler2 varchar(1),
    candidate_status varchar(1),
    street1 varchar(34),
    street2 varchar(34),
    city varchar(18),
    state varchar(2),
    zipcode varchar(5),
    committee_id varchar(9),
    election_year varchar(2),
    current_district varchar(2)
);

drop table if exists fec_committees;
create table fec_committees (
    committee_id varchar(9) PRIMARY KEY,
    committee_name varchar(90),
    treasurers_name varchar(38),
    street1 varchar(34),
    street2 varchar(34),
    city varchar(18),
    state varchar(2),
    zipcode varchar(5),
    committee_designation varchar(1),
    committee_type varchar(1),
    committee_party varchar(3),
    filing_frequency varchar(1),
    interest_group varchar(1),
    connected_org varchar(38),
    candidate_id varchar(9)
);

drop table if exists fec_indiv_import;
create table fec_indiv_import (
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
    date varchar(8),
    amount numeric(14,2),
    other_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);

drop table if exists fec_pac2cand_import;
create table fec_pac2cand_import (
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
    date varchar(8),
    amount numeric(14,2),
    other_id varchar(9),
    candidate_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);

drop table if exists fec_pac2pac_import;
CREATE TABLE fec_pac2pac_import (
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
    date varchar(8),
    amount numeric(14,2),
    other_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);

drop table if exists fec_candidate_summaries_import;
CREATE TABLE fec_candidate_summaries_import (
    candidate_id varchar(9) PRIMARY KEY,
    candidate_name varchar(38),
    incumbent_challenger_open varchar(1),
    party varchar(1),
    party_designation varchar(3),
    total_receipts integer,                             -- 22
    authorized_transfers_from integer,                  -- 18
    total_disbursements integer,                        -- 30
    transfers_to_authorized integer,                    -- 24
    beginning_cash integer,                             -- 6
    ending_cash integer,                                -- 10
    contributions_from_candidate integer,               -- 17d
    loans_from_candidate integer,                       -- 19a
    other_loans integer,                                -- 19b
    candidate_loan_repayments integer,                  -- 27a
    other_loan_repayments integer,                      -- 27b
    debts_owed_by integer,                              -- 12
    total_individual_contributions integer,             -- 17a
    state_code varchar(2),
    district varchar(2),
    special_election_status varchar(1),
    primary_election_status varchar(1),
    runoff_election_status varchar(1),
    general_election_status varchar(1),
    general_election_ct varchar(3),
    contributions_from_other_committees integer,        -- 17c
    contributions_from_party_committees integer,        -- 17b
    ending_date varchar(8),
    refunds_to_individuals integer,                     -- 28a
    refunds_to_committees integer                       -- 28b & 28c?
);

drop table if exists fec_committee_summaries_import;
CREATE TABLE fec_committee_summaries_import (
    committee_id VARCHAR(9) NOT NULL, 
    committee_name VARCHAR(90) NOT NULL, 
    committee_type VARCHAR(1) NOT NULL, 
    committee_designation VARCHAR(4), 
    filing_frequency VARCHAR(1) NOT NULL, 
    total_receipts INTEGER NOT NULL, 
    transfers_from_affiliates INTEGER NOT NULL, 
    individual_contributions INTEGER NOT NULL, 
    contributions_from_other_committees INTEGER NOT NULL, 
    contributions_from_candidate INTEGER NOT NULL, 
    candidate_loans INTEGER NOT NULL, 
    total_loans_received INTEGER NOT NULL, 
    total_disbursements INTEGER NOT NULL, 
    transfers_to_affiliates INTEGER NOT NULL, 
    refunds_to_individuals INTEGER NOT NULL, 
    refunds_to_committees INTEGER NOT NULL, 
    candidate_loan_repayments INTEGER NOT NULL, 
    loan_repayments INTEGER NOT NULL, 
    cash_beginning_of_year INTEGER NOT NULL, 
    cash_close_of_period INTEGER NOT NULL, 
    debts_owed INTEGER NOT NULL, 
    nonfederal_transfers_received INTEGER NOT NULL, 
    contributions_to_committees INTEGER NOT NULL, 
    independent_expenditures_made INTEGER NOT NULL, 
    party_coordinated_expenditures_made INTEGER NOT NULL, 
    nonfederal_expenditure_share INTEGER NOT NULL, 
    through_month VARCHAR(2) NOT NULL, 
    through_day VARCHAR(2) NOT NULL, 
    through_year INTEGER NOT NULL
);

