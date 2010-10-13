
\set agg_top_n 10

-- Lobbying View
-- Maps years to 2-year cycles and only includes valid reports

select date_trunc('second', now()) || ' -- drop view if exists lobbying_report';
drop view if exists lobbying_report;

select date_trunc('second', now()) || ' -- create view lobbying_report as';
create view lobbying_report as
    select *, case when year % 2 = 0 then year else year + 1 end as cycle
    from lobbying_lobbying l
    where
        use = 't';


-- Lobbying Client Associations

select date_trunc('second', now()) || ' -- drop table if exists assoc_lobbying_client';
drop table if exists assoc_lobbying_client;

select date_trunc('second', now()) || ' -- create table assoc_lobbying_client as';
create table assoc_lobbying_client as
    select a.entity_id, l.transaction_id
    from matchbox_entityalias a
    inner join matchbox_entity e
        on e.id = a.entity_id
    inner join lobbying_lobbying l
        on lower(a.alias) = lower(l.client_name)
    where
        a.verified = 't'
        and e.type = 'organization'

    union

    select a.entity_id, l.transaction_id
    from matchbox_entityattribute a
    inner join lobbying_lobbying l
        on a.value = l.client_ext_id
    where
        a.verified = 't'
        and a.namespace = 'urn:crp:organization'

    union all

    select ea.entity_id, l.transaction_id
    from matchbox_entityattribute ea
    inner join matchbox_entity e
        on e.id = ea.entity_id
    inner join agg_cat_map cm
        on ea.value = cm.catorder
    inner join lobbying_lobbying l
        on lower(cm.catcode) = lower(l.client_category)
    where
        ea.verified = 't'
        and e.type = 'industry'
;

select date_trunc('second', now()) || ' -- create index assoc_lobbying_client_entity_id on assoc_lobbying_client (entity_id)';
create index assoc_lobbying_client_entity_id on assoc_lobbying_client (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_lobbying_client_transaction_id on assoc_lobbying_client (transaction_id)';
create index assoc_lobbying_client_transaction_id on assoc_lobbying_client (transaction_id);


-- Lobbying Client Parent Associations

select date_trunc('second', now()) || ' -- drop table if exists assoc_lobbying_client_parent';
drop table if exists assoc_lobbying_client_parent;

select date_trunc('second', now()) || ' -- create table assoc_lobbying_client_parent as';
create table assoc_lobbying_client_parent as
    select a.entity_id, l.transaction_id
    from matchbox_entityalias a
    inner join matchbox_entity e
        on e.id = a.entity_id
    inner join lobbying_lobbying l
        on lower(a.alias) = lower(l.client_parent_name)
    where
        a.verified = 't'
        and e.type = 'organization';

select date_trunc('second', now()) || ' -- create index assoc_lobbying_client_parent_entity_id on assoc_lobbying_client_parent (entity_id)';
create index assoc_lobbying_client_parent_entity_id on assoc_lobbying_client_parent (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_lobbying_client_parent_transaction_id on assoc_lobbying_client_parent (transaction_id)';
create index assoc_lobbying_client_parent_transaction_id on assoc_lobbying_client_parent (transaction_id);


-- Lobbying Registrant Associations

select date_trunc('second', now()) || ' -- drop table if exists assoc_lobbying_registrant';
drop table if exists assoc_lobbying_registrant;

select date_trunc('second', now()) || ' -- create table assoc_lobbying_registrant as';
create table assoc_lobbying_registrant as
    select a.entity_id, l.transaction_id
    from matchbox_entityalias a
    inner join matchbox_entity e
        on e.id = a.entity_id
    inner join lobbying_lobbying l
        on lower(a.alias) = lower(l.registrant_name)
    where
        a.verified = 't'
        and e.type = 'organization';

select date_trunc('second', now()) || ' -- create index assoc_lobbying_registrant_entity_id on assoc_lobbying_registrant (entity_id)';
create index assoc_lobbying_registrant_entity_id on assoc_lobbying_registrant (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_lobbying_registrant_transaction_id on assoc_lobbying_registrant (transaction_id)';
create index assoc_lobbying_registrant_transaction_id on assoc_lobbying_registrant (transaction_id);


-- Lobbyist Associations

select date_trunc('second', now()) || ' -- drop table if exists assoc_lobbying_lobbyist';
drop table if exists assoc_lobbying_lobbyist;

select date_trunc('second', now()) || ' -- create table assoc_lobbying_lobbyist as';
create table assoc_lobbying_lobbyist as
    select a.entity_id, l.id
    from matchbox_entityattribute a
    inner join lobbying_lobbyist l
        on a.value = l.lobbyist_ext_id
    where
        a.verified = 't'
        and a.namespace = 'urn:crp:individual';

select date_trunc('second', now()) || ' -- create index assoc_lobbying_lobbyist_entity_id on assoc_lobbying_lobbyist (entity_id)';
create index assoc_lobbying_lobbyist_entity_id on assoc_lobbying_lobbyist (entity_id);
select date_trunc('second', now()) || ' -- create index assoc_lobbying_lobbyist_id on assoc_lobbying_lobbyist (id)';
create index assoc_lobbying_lobbyist_id on assoc_lobbying_lobbyist (id);


-- Total Spent

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_totals';
drop table if exists agg_lobbying_totals;

select date_trunc('second', now()) || ' -- create table agg_lobbying_totals as';
create table agg_lobbying_totals as
    select entity_id, coalesce(lobbyist.cycle, coalesce(firm.cycle, coalesce(non_firm_registrant.cycle, non_firm_client.cycle))) as cycle,
        coalesce(lobbyist.count, coalesce(firm.count, coalesce(non_firm_registrant.count, coalesce(non_firm_client.count, 0)))) as count,
        coalesce(non_firm_registrant.amount, coalesce(non_firm_client.amount, 0)) as non_firm_spending, coalesce(firm.amount, 0) as firm_income
    from
        (select entity_id, cycle, count(r)
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        group by entity_id, cycle) as lobbyist
    full outer join
        (select entity_id, cycle, count(r), sum(amount) as amount
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        inner join matchbox_organizationmetadata m using (entity_id)
        where
            m.lobbying_firm = 't'
        group by entity_id, cycle) as firm
    using (entity_id, cycle)
    full outer join
        (select entity_id, cycle, count(r), sum(amount) as amount
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        left join matchbox_organizationmetadata m using (entity_id)
        where
            coalesce(m.lobbying_firm, 'f') = 'f'
            and lower(r.registrant_name) = lower(r.client_name)
        group by entity_id, cycle) as non_firm_registrant
    using (entity_id, cycle)
    full outer join
        (select entity_id, cycle, count(r), sum(amount) as amount
        from lobbying_report r
        inner join assoc_lobbying_client ca using (transaction_id)
        left join matchbox_organizationmetadata m using (entity_id)
        left join matchbox_entity e on e.id = ca.entity_id
        where
            coalesce(m.lobbying_firm, 'f') = 'f'
            and case when e.type = 'industry' then r.include_in_industry_totals else 't' end
        group by entity_id, cycle) as non_firm_client
    using (entity_id, cycle)
union all
    select entity_id, -1,
        coalesce(lobbyist.count, coalesce(firm.count, coalesce(non_firm_registrant.count, coalesce(non_firm_client.count, 0)))) as count,
        coalesce(non_firm_registrant.amount, coalesce(non_firm_client.amount, 0)) as non_firm_spending, coalesce(firm.amount, 0) as firm_income
    from
        (select entity_id, count(r)
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        group by entity_id) as lobbyist
    full outer join
        (select entity_id, count(r), sum(amount) as amount
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        inner join matchbox_organizationmetadata m using (entity_id)
        where
            m.lobbying_firm = 't'
        group by entity_id) as firm
    using (entity_id)
    full outer join
        (select entity_id, count(r), sum(amount) as amount
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        left join matchbox_organizationmetadata m using (entity_id)
        where
            coalesce(m.lobbying_firm, 'f') = 'f'
            and lower(r.registrant_name) = lower(r.client_name)
        group by entity_id) as non_firm_registrant
    using (entity_id)
    full outer join
        (select entity_id, count(r), sum(amount) as amount
        from lobbying_report r
        inner join assoc_lobbying_client ca using (transaction_id)
        left join matchbox_organizationmetadata m using (entity_id)
        left join matchbox_entity e on e.id = ca.entity_id
        where
            coalesce(m.lobbying_firm, 'f') = 'f'
            and case when e.type = 'industry' then r.include_in_industry_totals else 't' end
        group by entity_id) as non_firm_client
    using (entity_id);

select date_trunc('second', now()) || ' -- create index agg_lobbying_totals_idx on agg_lobbying_totals (entity_id)';
create index agg_lobbying_totals_idx on agg_lobbying_totals (entity_id);


-- Firms Hired by Client
-- Note: We don't include records where the registrant_name = client_name. These don't represent an actual firm/client relationship,
-- they're just the way client firms report their overall spending.

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_registrants_for_client';
drop table if exists agg_lobbying_registrants_for_client;

select date_trunc('second', now()) || ' -- create table agg_lobbying_registrants_for_client as';
create table agg_lobbying_registrants_for_client as
    select client_entity, cycle, registrant_name, registrant_entity, count, amount
    from (select ca.entity_id as client_entity, r.cycle, r.registrant_name, ra.entity_id as registrant_entity, count(r), sum(amount) as amount,
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc, count(r) desc) as rank
        from lobbying_report r
        inner join (table assoc_lobbying_client union table assoc_lobbying_client_parent) as ca using (transaction_id)
        left join assoc_lobbying_registrant as ra using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where lower(registrant_name) != lower(client_name)
            and case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ca.entity_id, cycle, r.registrant_name, coalesce(ra.entity_id, '')) top
    where
        top.rank <= :agg_top_n
union all
    select client_entity, -1, registrant_name, registrant_entity, count, amount
    from (select ca.entity_id as client_entity, r.registrant_name, ra.entity_id as registrant_entity, count(r), sum(amount) as amount,
            rank() over (partition by ca.entity_id order by sum(amount) desc, count(r) desc) as rank
        from lobbying_report r
        inner join (table assoc_lobbying_client union table assoc_lobbying_client_parent) as ca using (transaction_id)
        left join assoc_lobbying_registrant as ra using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where lower(registrant_name) != lower(client_name)
            and case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ca.entity_id, r.registrant_name, coalesce(ra.entity_id, '')) top
    where
        top.rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_registrants_for_client_idx on agg_lobbying_registrants_for_client (client_entity, cycle)';
create index agg_lobbying_registrants_for_client_idx on agg_lobbying_registrants_for_client (client_entity, cycle);


-- Issues Lobbied by Client

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_issues_for_client';
drop table if exists agg_lobbying_issues_for_client;

select date_trunc('second', now()) || ' -- create table agg_lobbying_issues_for_client as';
create table agg_lobbying_issues_for_client as
    select client_entity, cycle, issue, count
    from (select ca.entity_id as client_entity, r.cycle, i.general_issue as issue, count(*),
            rank() over (partition by ca.entity_id, r.cycle order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join (table assoc_lobbying_client union table assoc_lobbying_client_parent) ca using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ca.entity_id, r.cycle, i.general_issue) top
    where
        rank <= :agg_top_n
union all
    select client_entity, -1, issue, count
    from (select ca.entity_id as client_entity, i.general_issue as issue, count(*),
            rank() over (partition by ca.entity_id order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join (table assoc_lobbying_client union table assoc_lobbying_client_parent) ca using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ca.entity_id, i.general_issue) top
    where
        rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_issues_for_client_idx on agg_lobbying_issues_for_client (client_entity, cycle)';
create index agg_lobbying_issues_for_client_idx on agg_lobbying_issues_for_client (client_entity, cycle);


-- Lobbyists Working for Client

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_lobbyists_for_client';
drop table if exists agg_lobbying_lobbyists_for_client;

select date_trunc('second', now()) || ' -- create table agg_lobbying_lobbyists_for_client as';
create table agg_lobbying_lobbyists_for_client as
    select client_entity, cycle, lobbyist_name, lobbyist_entity, count
    from (select ca.entity_id as client_entity, r.cycle, l.lobbyist_name, la.entity_id as lobbyist_entity, count(*),
            rank() over (partition by ca.entity_id, r.cycle order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join (table assoc_lobbying_client union table assoc_lobbying_client_parent) ca using (transaction_id)
        left join assoc_lobbying_lobbyist la using (id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ca.entity_id, r.cycle, l.lobbyist_name, coalesce(la.entity_id, '')) top
    where
        rank <= :agg_top_n
union all
    select client_entity, -1, lobbyist_name, lobbyist_entity, count
    from (select ca.entity_id as client_entity, l.lobbyist_name, la.entity_id as lobbyist_entity, count(*),
            rank() over (partition by ca.entity_id order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join (table assoc_lobbying_client union table assoc_lobbying_client_parent) ca using (transaction_id)
        left join assoc_lobbying_lobbyist la using (id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ca.entity_id, l.lobbyist_name, coalesce(la.entity_id, '')) top
    where
        rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_lobbyists_for_client_idx on agg_lobbying_lobbyists_for_client (client_entity, cycle)';
create index agg_lobbying_lobbyists_for_client_idx on agg_lobbying_lobbyists_for_client (client_entity, cycle);


-- Firms Employing a Lobbyist

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_registrants_for_lobbyist';
drop table if exists agg_lobbying_registrants_for_lobbyist;

select date_trunc('second', now()) || ' -- create table agg_lobbying_registrants_for_lobbyist as';
create table agg_lobbying_registrants_for_lobbyist as
    select top.lobbyist_entity, top.cycle, top.registrant_name, top.registrant_entity, top.count
    from (select la.entity_id as lobbyist_entity, r.cycle, r.registrant_name, ra.entity_id as registrant_entity, count(r),
            rank() over (partition by la.entity_id, cycle order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_registrant ra using (transaction_id)
        group by la.entity_id, cycle, r.registrant_name, ra.entity_id) top
    where
        top.rank <= :agg_top_n
union all
    select top.lobbyist_entity, -1, top.registrant_name, top.registrant_entity, top.count
    from (select la.entity_id as lobbyist_entity, r.registrant_name, ra.entity_id as registrant_entity, count(r),
            rank() over (partition by la.entity_id order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_registrant ra using (transaction_id)
        group by la.entity_id, r.registrant_name, ra.entity_id) top
    where
        top.rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_registrants_for_lobbyist_idx on agg_lobbying_registrants_for_lobbyist (lobbyist_entity, cycle)';
create index agg_lobbying_registrants_for_lobbyist_idx on agg_lobbying_registrants_for_lobbyist (lobbyist_entity, cycle);


-- Issues Worked on by a Lobbyist

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_issues_for_lobbyist';
drop table if exists agg_lobbying_issues_for_lobbyist;

select date_trunc('second', now()) || ' -- create table agg_lobbying_issues_for_lobbyist as';
create table agg_lobbying_issues_for_lobbyist as
    select lobbyist_entity, cycle, issue, count
    from (select la.entity_id as lobbyist_entity, r.cycle, i.general_issue as issue, count(r),
            rank() over (partition by la.entity_id, r.cycle order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la on la.id = l.id
        group by la.entity_id, r.cycle, i.general_issue) top
    where
        rank <= :agg_top_n
union all
    select lobbyist_entity, -1, issue, count
    from (select la.entity_id as lobbyist_entity, i.general_issue as issue, count(r),
            rank() over (partition by la.entity_id order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la on la.id = l.id
        group by la.entity_id, i.general_issue) top
    where
        rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_issues_for_lobbyist_idx on agg_lobbying_issues_for_lobbyist (lobbyist_entity, cycle)';
create index agg_lobbying_issues_for_lobbyist_idx on agg_lobbying_issues_for_lobbyist (lobbyist_entity, cycle);


-- Clients of a Lobbyist

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_clients_for_lobbyist';
drop table if exists agg_lobbying_clients_for_lobbyist;

select date_trunc('second', now()) || ' -- create table agg_lobbying_clients_for_lobbyist as';
create table agg_lobbying_clients_for_lobbyist as
    select lobbyist_entity, cycle, client_name, client_entity, count
    from (select la.entity_id as lobbyist_entity, r.cycle, r.client_name, ca.entity_id as client_entity, count(r),
            rank() over (partition by la.entity_id, r.cycle order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_client ca using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by la.entity_id, r.cycle, r.client_name, coalesce(ca.entity_id, '')) top
    where
        rank <= :agg_top_n
union all
    select lobbyist_entity, -1, client_name, client_entity, count
    from (select la.entity_id as lobbyist_entity, r.client_name, ca.entity_id as client_entity, count(r),
            rank() over (partition by la.entity_id order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_client ca using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by la.entity_id, r.client_name, coalesce(ca.entity_id, '')) top
    where
        rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_clients_for_lobbyist_idx on agg_lobbying_clients_for_lobbyist (lobbyist_entity, cycle)';
create index agg_lobbying_clients_for_lobbyist_idx on agg_lobbying_clients_for_lobbyist (lobbyist_entity, cycle);


-- Clients of a Lobbying Firm


select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_clients_for_registrant';
drop table if exists agg_lobbying_clients_for_registrant;

select date_trunc('second', now()) || ' -- create table agg_lobbying_clients_for_registrant as';
create table agg_lobbying_clients_for_registrant as
    select registrant_entity, cycle, client_name, client_entity, count, amount
    from (select ra.entity_id as registrant_entity, r.cycle, r.client_name, ca.entity_id as client_entity, count(r), sum(amount) as amount,
            rank() over (partition by ra.entity_id, r.cycle order by sum(amount) desc, count(r) desc) as rank
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        left join assoc_lobbying_client ca using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ra.entity_id, r.cycle, r.client_name, coalesce(ca.entity_id, '')) top
    where
        rank <= :agg_top_n
union all
    select registrant_entity, -1, client_name, client_entity, count, amount
    from (select ra.entity_id as registrant_entity, r.client_name, ca.entity_id as client_entity, count(r), sum(amount) as amount,
            rank() over (partition by ra.entity_id order by sum(amount) desc, count(r) desc) as rank
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        left join assoc_lobbying_client ca using (transaction_id)
        left join matchbox_entity ce on ce.id = ca.entity_id
        where case when ce.type = 'industry' then r.include_in_industry_totals else 't' end
        group by ra.entity_id, r.client_name, coalesce(ca.entity_id, '')) top
    where
        rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_clients_for_registrant_idx on agg_lobbying_clients_for_registrant (registrant_entity, cycle)';
create index agg_lobbying_clients_for_registrant_idx on agg_lobbying_clients_for_registrant (registrant_entity, cycle);


-- Issues on which a Firm Works

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_issues_for_registrant';
drop table if exists agg_lobbying_issues_for_registrant;

select date_trunc('second', now()) || ' -- create table agg_lobbying_issues_for_registrant as';
create table agg_lobbying_issues_for_registrant as
    select registrant_entity, cycle, issue, count
    from (select ra.entity_id as registrant_entity, r.cycle, i.general_issue as issue, count(r),
            rank() over (partition by ra.entity_id, r.cycle order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join assoc_lobbying_registrant ra using (transaction_id)
        group by ra.entity_id, r.cycle, i.general_issue) top
    where
        rank <= :agg_top_n
union all
    select registrant_entity, -1, issue, count
    from (select ra.entity_id as registrant_entity, i.general_issue as issue, count(r),
            rank() over (partition by ra.entity_id order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join assoc_lobbying_registrant ra using (transaction_id)
        group by ra.entity_id, i.general_issue) top
    where
        rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_issues_for_registrant_idx on agg_lobbying_issues_for_registrant (registrant_entity, cycle)';
create index agg_lobbying_issues_for_registrant_idx on agg_lobbying_issues_for_registrant (registrant_entity, cycle);


-- Lobbyists Employed by a Firm

select date_trunc('second', now()) || ' -- drop table if exists agg_lobbying_lobbyists_for_registrant';
drop table if exists agg_lobbying_lobbyists_for_registrant;

select date_trunc('second', now()) || ' -- create table agg_lobbying_lobbyists_for_registrant as';
create table agg_lobbying_lobbyists_for_registrant as
    select registrant_entity, cycle, lobbyist_name, lobbyist_entity, count
    from (select ra.entity_id as registrant_entity, r.cycle, l.lobbyist_name, la.entity_id as lobbyist_entity, count(r),
            rank() over (partition by ra.entity_id, cycle order by count(r) desc) as rank
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        inner join lobbying_lobbyist l using (transaction_id)
        left join assoc_lobbying_lobbyist la using (id)
        group by ra.entity_id, cycle, l.lobbyist_name, la.entity_id) top
    where
        top.rank <= :agg_top_n
union all
    select registrant_entity, -1, lobbyist_name, lobbyist_entity, count
    from (select ra.entity_id as registrant_entity, l.lobbyist_name, la.entity_id as lobbyist_entity, count(r),
            rank() over (partition by ra.entity_id order by count(r) desc) as rank
        from lobbying_report r
        inner join assoc_lobbying_registrant ra using (transaction_id)
        inner join lobbying_lobbyist l using (transaction_id)
        left join assoc_lobbying_lobbyist la using (id)
        group by ra.entity_id, l.lobbyist_name, la.entity_id) top
    where
        top.rank <= :agg_top_n;

select date_trunc('second', now()) || ' -- create index agg_lobbying_lobbyists_for_registrant_idx on agg_lobbying_lobbyists_for_registrant (lobbyist_entity, cycle)';
create index agg_lobbying_lobbyists_for_registrant_idx on agg_lobbying_lobbyists_for_registrant (lobbyist_entity, cycle);
