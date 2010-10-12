drop table matchbox_currentrace;

create table matchbox_currentrace as
    select e.id, e.name, recipient_state as state, election_type, district, seat, seat_status, seat_result
    from recipient_associations a
    inner join matchbox_entity e on e.id = a.entity_id
    inner join contribution_contribution c using (transaction_id)
    where 
        cycle = 2010
        and e.type = 'politician'
        and seat in ('federal:senate', 'federal:house', 'state:governor')
    group by e.id, e.name, recipient_state, election_type, district, seat, seat_status, seat_result;
