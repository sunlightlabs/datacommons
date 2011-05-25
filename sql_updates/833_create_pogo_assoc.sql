create table assoc_pogo (entity_id uuid, misconduct_id integer);
insert into assoc_pogo (entity_id, misconduct_id)
    select distinct match_id, misconduct.id
    from matching_pogo_matches_20110520_1717 matches
    inner join pogo_misconduct misconduct
    on subject_id = contractor_id
    where confidence > 2;
