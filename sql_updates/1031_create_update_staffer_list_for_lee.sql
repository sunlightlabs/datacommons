drop table staffer_matches_for_lee;
create table staffer_matches_for_lee as
select subject_id,
    assoc_lob.entity_id,
    confidence,
    mlob.name as staffer_name,
    lobbyist_name,
    registrant_name,
    client_name,
    client_parent_name,
    client_category as client_industry_code,
    sum(amount) as total_for_contracts
from staffers_matches_20120119_1454 m
inner join assoc_lobbying_lobbyist assoc_lob on m.match_id = assoc_lob.entity_id
inner join lobbying_lobbyist llob on assoc_lob.id = llob.id
inner join lobbying_report lb using (transaction_id)
inner join matchbox_entity mlob on mlob.id = m.match_id
where
    use = 't'
group by
    subject_id, assoc_lob.entity_id, confidence, mlob.name, lobbyist_name, registrant_name, client_name, client_parent_name, client_category
;

