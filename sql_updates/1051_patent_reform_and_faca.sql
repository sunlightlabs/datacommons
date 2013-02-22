select 'Corporate entities and their committee memberships during 2011';
select me.id, me.name, trim(trailing from committeename), count(distinct fm.firstname || ' ' || fm.lastname) as number_of_members
from faca_matches
inner join faca_members fm using (membersid)
inner join faca_committees fc using (cid)
inner join faca_agencies fa using (aid)
inner join matchbox_entity me on entity_id = me.id
where
    entity_id in (
        '29d47a775c5f4f4ea6ca51a3a87aea47',
        'f1244474fad44ad9a3a57859b4a709b1',
        '329c4520cfbe49d098fb3b26aee07fe3',
        'd44ed3cafeee49a1a6e943c7d61ee2cc',
        '5393e8ca82a04d13b2fa699b4ec59291',
        'c9af1097a27f450bb897e5b87739dbea',
        '51776e4b60214502bda68c6a7160c497'
    )
    and (
        (enddate = '') or (2011 between extract(year from startdate::date) and extract(year from enddate::date) and startdate != '')
    )
    and (
        fa.agencyabbr = 'DOC'
    )
group by me.id, me.name, committeename;


select 'Lobbying shops and their committee memberships during 2011';
select me.id, me.name, trim(trailing from committeename), count(distinct fm.firstname || ' ' || fm.lastname) as number_of_members
from faca_matches
inner join faca_members fm using (membersid)
inner join faca_committees fc using (cid)
inner join faca_agencies fa using (aid)
inner join matchbox_entity me on entity_id = me.id
where
    entity_id in (
        '10bfec65f9af4d7794c28d8cd7454596',
        '3da0b87ca8d34652b2fde3231d524c12',
        '8595a50e311d4b2fbca37ca0b1367676',
        'c731bfe879c44d6fae99d482d04f1c57',
        '8595a50e311d4b2fbca37ca0b1367676',
        'ffae539a60054b4d9e300e729baa268f'
    )
    and (
        (enddate = '') or (2011 between extract(year from startdate::date) and extract(year from enddate::date) and startdate != '')
    )
    and fa.agencyabbr = 'DOC'
group by me.id, me.name, committeename;

