
drop table if exists fec_candidates_import;
create table fec_candidates_import (
    candidate_id varchar(9) PRIMARY KEY,
    candidate_name varchar(200),
    party varchar(3),
    election_year integer,
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
    zipcode varchar(9)
);

drop table if exists fec_committees;
create table fec_committees (
    committee_id varchar(9) PRIMARY KEY,
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

drop table if exists fec_candidate_summaries;
CREATE TABLE fec_candidate_summaries (
    candidate_id varchar(9) PRIMARY KEY,
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
    refunds_to_committees numeric(14,2)                      -- 28b & 28c?
);

drop table if exists fec_committee_summaries;
CREATE TABLE fec_committee_summaries (
    committee_id varchar(9) PRIMARY KEY,
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
    through_date date
);

