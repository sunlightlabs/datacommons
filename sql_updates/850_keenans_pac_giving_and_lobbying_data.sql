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

