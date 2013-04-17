drop view contribution_dc;
create view contribution_dc as 
    select
        transaction_id,
        'urn:dc:transaction'::varchar(32) as transaction_namespace,
        recipient_name,
        committee_name,
        contributor_name,
        contributor_entity,
        contributor_type,
        contributor_type_internal,
        payment_type,
        contributor_address,
        contributor_city,
        contributor_state,
        contributor_zipcode,
        amount,
        date,
        party as recipient_party,
        'DC'::varchar(2) as recipient_state,
        office as seat,
        ward
    from contribution_contributiondc c 
    left join dc_committee_candidate cc on cc.committee = c.committee_name
    left join dc_candidate_metadata m on m.id = cc.id and date between m.from_date and m.to_date
;
