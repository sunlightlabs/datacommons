
\set agg_top_n 10

-- Lobbying View
-- Maps years to 2-year cycles and only includes valid reports

drop view if exists lobbying_report;

create view lobbying_report as
    select *, case when year % 2 = 0 then year else year + 1 end as cycle
    from lobbying_lobbying l
    where
        use = 't';


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
    

-- Firms Hired by Client    
    
drop table if exists agg_lobbying_registrants_for_client;

create table agg_lobbying_registrants_for_client as
    select top.client_entity, top.cycle, top.registrant_name, top.registrant_entity, top.amount
    from (select ca.entity_id as client_entity, r.cycle, r.registrant_name, coalesce(ra.entity_id, '') as registrant_entity, sum(amount) as amount, 
            rank() over (partition by ca.entity_id, cycle order by sum(amount) desc) as rank
        from lobbying_report r
        inner join assoc_lobbying_client as ca using (transaction_id)
        left join assoc_lobbying_registrant as ra using (transaction_id)
        group by ca.entity_id, cycle, r.registrant_name, coalesce(ra.entity_id, '')) top
    where
        top.rank <= :agg_top_n
union
    select top.client_entity, -1, top.registrant_name, top.registrant_entity, top.amount
    from (select ca.entity_id as client_entity, r.registrant_name, coalesce(ra.entity_id, '') as registrant_entity, sum(amount) as amount, 
            rank() over (partition by ca.entity_id order by sum(amount) desc) as rank
        from lobbying_report r
        inner join assoc_lobbying_client as ca using (transaction_id)
        left join assoc_lobbying_registrant as ra using (transaction_id)
        group by ca.entity_id, r.registrant_name, coalesce(ra.entity_id, '')) top
    where
        top.rank <= :agg_top_n;
        
create index agg_lobbying_registrants_for_client_idx on agg_lobbying_registrants_for_client (client_entity, cycle);


-- Issues Lobbied by Client

drop table if exists agg_lobbying_issues_for_client;

create table agg_lobbying_issues_for_client as
    select client_entity, cycle, issue, count
    from (select ca.entity_id as client_entity, r.cycle, i.general_issue as issue, count(*),
            rank() over (partition by ca.entity_id, r.cycle order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join assoc_lobbying_client ca using (transaction_id)
        group by ca.entity_id, r.cycle, i.general_issue) top
    where
        rank <= :agg_top_n
union
    select client_entity, -1, issue, count
    from (select ca.entity_id as client_entity, i.general_issue as issue, count(*),
            rank() over (partition by ca.entity_id order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_issue i using (transaction_id)
        inner join assoc_lobbying_client ca using (transaction_id)
        group by ca.entity_id, i.general_issue) top
    where
        rank <= :agg_top_n;

create index agg_lobbying_issues_for_client_idx on agg_lobbying_issues_for_client (client_entity, cycle);


-- Lobbyists Working for Client

drop table if exists agg_lobbying_lobbyists_for_client;

create table agg_lobbying_lobbyists_for_client as
    select client_entity, cycle, lobbyist_name, lobbyist_entity, count
    from (select ca.entity_id as client_entity, r.cycle, l.lobbyist_name, coalesce(la.entity_id, '') as lobbyist_entity, count(*),
            rank() over (partition by ca.entity_id, r.cycle order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_client ca using (transaction_id)
        left join assoc_lobbying_lobbyist la using (id)
        group by ca.entity_id, r.cycle, l.lobbyist_name, coalesce(la.entity_id, '')) top
    where
        rank <= :agg_top_n
union
    select client_entity, -1, lobbyist_name, lobbyist_entity, count
    from (select ca.entity_id as client_entity, l.lobbyist_name, coalesce(la.entity_id, '') as lobbyist_entity, count(*),
            rank() over (partition by ca.entity_id order by count(*) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_client ca using (transaction_id)
        left join assoc_lobbying_lobbyist la using (id)
        group by ca.entity_id, l.lobbyist_name, coalesce(la.entity_id, '')) top
    where
        rank <= :agg_top_n;
        
create index agg_lobbying_lobbyists_for_client_idx on agg_lobbying_lobbyists_for_client (client_entity, cycle);
    

-- Firms Employing a Lobbyist

drop table if exists agg_lobbying_registrants_for_lobbyist;

create table agg_lobbying_registrants_for_lobbyist as
    select top.lobbyist_entity, top.cycle, top.registrant_name, top.registrant_entity, top.count
    from (select la.entity_id as lobbyist_entity, r.cycle, r.registrant_name, coalesce(ra.entity_id, '') as registrant_entity, count(r), 
            rank() over (partition by la.entity_id, cycle order by count(r) desc) as rank            
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_registrant ra using (transaction_id)
        group by la.entity_id, cycle, r.registrant_name, coalesce(ra.entity_id, '')) top
    where
        top.rank <= :agg_top_n
union
    select top.lobbyist_entity, -1, top.registrant_name, top.registrant_entity, top.count
    from (select la.entity_id as lobbyist_entity, r.registrant_name, coalesce(ra.entity_id, '') as registrant_entity, count(r), 
            rank() over (partition by la.entity_id order by count(r) desc) as rank            
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_registrant ra using (transaction_id)
        group by la.entity_id, r.registrant_name, coalesce(ra.entity_id, '')) top
    where
        top.rank <= :agg_top_n; 

create index agg_lobbying_registrants_for_lobbyist_idx on agg_lobbying_registrants_for_lobbyist (lobbyist_entity, cycle);


-- Issues Worked on by a Lobbyist

drop table if exists agg_lobbying_issues_for_lobbyist;

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
union
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

create index agg_lobbying_issues_for_lobbyist_idx on agg_lobbying_issues_for_lobbyist (lobbyist_entity, cycle);


-- Clients of a Lobbyist

drop table if exists agg_lobbying_clients_for_lobbyist;

create table agg_lobbying_clients_for_lobbyist as
    select lobbyist_entity, cycle, client_name, client_entity, count
    from (select la.entity_id as lobbyist_entity, r.cycle, r.client_name, coalesce(ca.entity_id, '') as client_entity, count(r),
            rank() over (partition by la.entity_id, r.cycle order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_client ca using (transaction_id)
        group by la.entity_id, r.cycle, r.client_name, coalesce(ca.entity_id, '')) top
    where
        rank <= :agg_top_n
union
    select lobbyist_entity, -1, client_name, client_entity, count
    from (select la.entity_id as lobbyist_entity, r.client_name, coalesce(ca.entity_id, '') as client_entity, count(r),
            rank() over (partition by la.entity_id order by count(r) desc) as rank
        from lobbying_report r
        inner join lobbying_lobbyist l using (transaction_id)
        inner join assoc_lobbying_lobbyist la using (id)
        left join assoc_lobbying_client ca using (transaction_id)
        group by la.entity_id, r.client_name, coalesce(ca.entity_id, '')) top
    where
        rank <= :agg_top_n;
        
create index agg_lobbying_clients_for_lobbyist_idx on agg_lobbying_clients_for_lobbyist (lobbyist_entity, cycle);
        