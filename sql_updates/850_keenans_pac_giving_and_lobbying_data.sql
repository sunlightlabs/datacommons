-- Organization PAC Giving


select date_trunc('second', now()) || ' -- drop table if exists agg_org_pac_total';
drop table if exists agg_org_pac_total;

select date_trunc('second', now()) || ' -- create table agg_org_pac_total';
create table agg_org_pac_total as
    select
        ca.entity_id,
        oe.name as organization_name,
        cycle,
        count(*),
        sum(c.amount) as amount
    from contributions_organization c
    inner join recipient_associations ra using (transaction_id)
    left join contributor_associations ca using (transaction_id)
    inner join matchbox_entity oe on oe.id = ca.entity_id
    group by ca.entity_id, oe.name, cycle
;

select date_trunc('second', now()) || ' -- create index agg_org_pac_total__entity_id';
create index agg_org_pac_total__entity_id on agg_org_pac_total (entity_id);


select
    hr.registrant_ext_id,
    hr.name,
    e.name,
    hr.total_given,
    pt.amount as total_pac_giving,
    l.total_lobbying,
    m.confidence
from
    honorarium_registrant hr
    left join ks_matches_20110531_1518 m on hr.id = m.subject_id
    left join matchbox_entity e on m.match_id = e.id
    left join agg_org_pac_total pt on pt.entity_id = m.match_id
    left join (
        select
            r.entity_id,
            year + year % 2 as cycle,
            sum(l.amount) as total_lobbying
        from assoc_lobbying_registrant r
        left join lobbying_lobbying l using (transaction_id)
        group by r.entity_id, cycle
    ) l using (entity_id, cycle)
where
    (cycle is null or cycle = 2010)
order by
    hr.id;

