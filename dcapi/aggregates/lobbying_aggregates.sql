

-- Lobbying Client Associations

drop table if exists assoc_lobbying_client;

create table assoc_lobbying_client as
    select a.entity_id, l.transaction_id
    from matchbox_entityalias a
    inner join lobbying_lobbying l
        on a.alias = l.client_name or a.alias = l.client_parent_name
    where
        a.verified = 't'
union
    select a.entity_id, l.transaction_id
    from matchbox_entityattribute a
    inner join lobbying_lobbying l
        on a.value = l.client_ext_id
    where
        a.verified = 't'
        and a.namespace = 'urn:crp:organization';

create index assoc_lobbying_client_entity_id on assoc_lobbying_client (entity_id);
create index assoc_lobbying_client_transaction_id on assoc_lobbying_client (transaction_id);


-- Lobbying Registrant Associations

drop table if exists assoc_lobbying_registrant;

create table assoc_lobbying_registrant as
    select a.entity_id, l.transaction_id
    from matchbox_entityalias a
    inner join lobbying_lobbying l
        on a.alias = l.registrant_name
    where
        a.verified = 't';

create index assoc_lobbying_registrant_entity_id on assoc_lobbying_registrant (entity_id);
create index assoc_lobbying_registrant_transaction_id on assoc_lobbying_registrant (transaction_id);


-- Lobbyist Associations

drop table if exists assoc_lobbying_lobbyist;

create table assoc_lobbying_lobbyist as
    select a.entity_id, l.id
    from matchbox_entityalias a
    inner join lobbying_lobbyist l
        on a.alias = l.lobbyist_name
    where
        a.verified = 't'
union
    select a.entity_id, l.id
    from matchbox_entityattribute a
    inner join lobbying_lobbyist l
        on a.value = l.lobbyist_ext_id
    where
        a.verified = 't'
        and a.namespace = 'urn:crp:individual';

create index assoc_lobbying_lobbyist_entity_id on assoc_lobbying_lobbyist (entity_id);
create index assoc_lobbying_lobbyist_id on assoc_lobbying_lobbyist (id);


-- Lobbyist Candidate Associations

drop table if exists assoc_lobbying_lobbyist_candidate;

create table assoc_lobbying_lobbyist_candidate as
    select a.entity_id, l.id
    from matchbox_entityattribute a
    inner join lobbying_lobbyist l
        on a.value = l.candidate_ext_id
    where
        a.verified = 't'
        and a.namespace = 'urn:crp:recipient';

create index assoc_lobbying_lobbyist_candidate_entity_id on assoc_lobbying_lobbyist_candidate (entity_id);
create index assoc_lobbying_lobbyist_candidate_id on assoc_lobbying_lobbyist_candidate (id);
