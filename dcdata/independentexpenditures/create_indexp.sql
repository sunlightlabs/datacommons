
drop table if exists fec_indexp_import;
create table fec_indexp_import (
    candidate_id varchar(9),
    candidate_name varchar(90),
    spender_id varchar(9),
    spender_name varchar(90),
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
    prev_file_num varchar(6)
);


