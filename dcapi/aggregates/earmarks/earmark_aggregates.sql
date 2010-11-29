-- Member associations

select date_trunc('second', now()) || ' -- drop table if exists earmarks_member_associations';
drop table if exists earmarks_member_associations;

select date_trunc('second', now()) || ' -- create table earmarks_member_associations';
create table earmarks_member_associations as
    select
        ea.entity_id,
        m.earmark_id
    from earmarks_member m
    inner join matchbox_entityattribute ea
        on m.crp_id = ea.value
    where
        ea.namespace = 'urn:crp:recipient'
    ;

select date_trunc('second', now()) || ' -- create index earmarks_member_associations_entity_id on earmarks_member_associations (entity_id)';
create index earmarks_member_associations_entity_id on earmarks_member_associations (entity_id);
select date_trunc('second', now()) || ' -- create index earmarks_member_associations_earmark_id on earmarks_member_associations (earmark_id)';
create index earmarks_member_associations_earmark_id on earmarks_member_associations (earmark_id);


-- Recipient Associations

select date_trunc('second', now()) || ' -- drop table if exists earmarks_recipient_associations';
drop table if exists earmarks_recipient_associations;

select date_trunc('second', now()) || ' -- create table earmarks_recipient_associations';
create table earmarks_recipient_associations as
    select
        e.id as entity_id,
        r.earmark_id
    from earmarks_recipient r
    inner join matchbox_entity e
        on e.name = r.standardized_recipient
    where
        e.type = 'organization'
    ;

select date_trunc('second', now()) || ' -- create index earmarks_recipient_associations_entity_id on earmarks_recipient_associations (entity_id)';
create index earmarks_recipient_associations_entity_id on earmarks_recipient_associations (entity_id);
select date_trunc('second', now()) || ' -- create index earmarks_recipient_associations_earmark_id on earmarks_recipient_associations (earmark_id)';
create index earmarks_recipient_associations_earmark_id on earmarks_recipient_associations (earmark_id);


