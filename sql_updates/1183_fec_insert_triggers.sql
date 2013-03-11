create trigger insert_fec_candidates_trigger
    before insert on fec_candidates
    for each row execute procedure fec_candidates_insert_trigger();


create trigger insert_fec_committees_trigger
    before insert on fec_committees
    for each row execute procedure fec_committees_insert_trigger();


create trigger insert_fec_indiv_trigger
    before insert on fec_indiv
    for each row execute procedure fec_indiv_insert_trigger();


create trigger insert_fec_pac2cand_trigger
    before insert on fec_pac2cand
    for each row execute procedure fec_pac2cand_insert_trigger();


create trigger insert_fec_pac2pac_trigger
    before insert on fec_pac2pac
    for each row execute procedure fec_pac2pac_insert_trigger();


create trigger insert_fec_candidate_summaries_trigger
    before insert on fec_candidate_summaries
    for each row execute procedure fec_candidate_summaries_insert_trigger();


create trigger insert_fec_committee_summaries_trigger
    before insert on fec_committee_summaries
    for each row execute procedure fec_committee_summaries_insert_trigger();
