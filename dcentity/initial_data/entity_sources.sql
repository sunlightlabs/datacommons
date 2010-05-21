


-- Individual Entities

create table tmp_individuals as
    select min(lobbyist_name) as name, lobbyist_ext_id as id
    from lobbying_lobbyist
    where
        lobbyist_name != ''
    group by lobbyist_ext_id
union
    select min(contributor_name) as name, contributor_ext_id as id
    from contribution_contribution
    where
        contributor_name != ''
        and contributor_ext_id like 'U%'
        and not exists (select * from lobbying_lobbyist where lobbyist_ext_id = contributor_ext_id)
    group by contributor_ext_id;
    


-- Politician Entities

create table tmp_politicians as
    select min(recipient_name) as name, transaction_namespace as namespace, recipient_ext_id as id
    from contribution_contribution
    where
        recipient_type = 'P'
        and recipient_name != ''
    group by transaction_namespace, recipient_ext_id;