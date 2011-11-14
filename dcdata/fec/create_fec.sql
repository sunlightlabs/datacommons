
drop table if exists fec_candidates;
create table fec_candidates (
    candidate_id varchar(9) PRIMARY KEY,
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
    election_type varchar(1),
    microfilm_location varchar(11),
    transaction_type varchar(3),
    contributor_lender_transfer varchar(34),
    city varchar(18),
    state varchar(2),
    zipcode varchar(5),
    occupation varchar(35),
    transaction_month varchar(2),
    transaction_day varchar(2),
    transaction_century varchar(2),
    transaction_year varchar(2),
    amount varchar(7),
    other_id varchar(9),
    fec_record varchar(7)
);

drop table if exists fec_pac2cand_import;
create table fec_pac2cand_import (
	filer_id VARCHAR(9), 
	amendment VARCHAR(1), 
	report_type VARCHAR(3), 
	election_type VARCHAR(1), 
	microfilm_location VARCHAR(11), 
	transaction_type VARCHAR(3), 
	transaction_month VARCHAR(2), 
	transaction_day VARCHAR(2), 
	transaction_century VARCHAR(2), 
	transaction_year VARCHAR(2), 
	amount VARCHAR(7), 
	other_id VARCHAR(9), 
	candidate_id VARCHAR(9), 
	fec_record VARCHAR(7)
);

drop table if exists fec_pac2pac_import;
CREATE TABLE fec_pac2pac_import (
	filer_id VARCHAR(9), 
	amendment VARCHAR(1), 
	report_type VARCHAR(3), 
	election_type VARCHAR(1), 
	microfilm_location VARCHAR(11), 
	transaction_type VARCHAR(3), 
	contributor_lender_transfer VARCHAR(34), 
	city VARCHAR(18), 
	state VARCHAR(2), 
	zipcode VARCHAR(5), 
	occupation VARCHAR(35), 
	transaction_month VARCHAR(2), 
	transaction_day VARCHAR(2), 
	transaction_century VARCHAR(2), 
	transaction_year VARCHAR(2), 
	amount VARCHAR(7), 
	other_id VARCHAR(9), 
	fec_record VARCHAR(7)
);





