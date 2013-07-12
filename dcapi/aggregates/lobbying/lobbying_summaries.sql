 -- Top 10 Parentmost Clients for Top 10 Lobbying Issues by Amount
 
  select date_trunc('second', now()) || ' -- drop table if exists summary_lobbying_top_biggest_orgs_for_top_issues';
  drop table if exists summary_lobbying_top_biggest_orgs_for_top_issues;
  
  select date_trunc('second', now()) || ' -- create table summary_lobbying_top_biggest_orgs_for_top_issues';
  create table summary_lobbying_top_biggest_orgs_for_top_issues as
       select bo.cycle, bo.general_issue as issue, me.name, bo.client_entity as id, bo.count as client_count, bo.rank_by_count as client_rank_by_count, bo.amount as client_amount, bo.rank_by_amount as client_rank_by_amount, li.count as issue_total_count, li.rank_by_count as issue_rank_by_count, li.amount as issue_total_amount, li.rank_by_amount as issue_rank_by_amount
        from 
            agg_lobbying_issues_across_biggest_orgs li
          inner join
            agg_lobbying_biggest_orgs_for_issues bo on bo.general_issue =  li.general_issue and bo.cycle = li.cycle
          inner join
            matchbox_entity me on me.id = bo.client_entity
        where bo.rank_by_amount <= 10 and li.rank_by_amount <= 10
        order by cycle, issue_rank_by_amount, client_rank_by_amount;

  select date_trunc('second', now()) || ' -- create index summary_lobbying_top_biggest_orgs_for_top_issues_idx on summary_lobbying_top_biggest_orgs_for_top_issues (cycle, rank_by_amount)';
  create index summary_lobbying_top_biggest_orgs_for_top_issues_idx on summary_lobbying_top_biggest_orgs_for_top_issues (issue, cycle);

--  Ranking Biggest Client Lobbyied Bills by Amount and Count
 
 select date_trunc('second', now()) || ' -- drop table if exists summary_lobbying_bills_for_biggest_org';
 drop table if exists summary_lobbying_bills_for_biggest_org;
 
 select date_trunc('second', now()) || ' -- create table summary_lobbying_bills_for_biggest_org as';
 create table summary_lobbying_bills_for_biggest_org as
     with lobbying_by_cycle as (
        select client_name, client_entity, congress_no, bill_id, bill_name, bill_type, bill_no, cycle, count, amount,
             rank() over (partition by congress_no, bill_id order by amount desc) as rank_by_amount,
             rank() over (partition by congress_no, bill_id order by count desc) as rank_by_count
        from 
         (select
             ce.name as client_name,
             ca.entity_id as client_entity,
             b.bill_id,
             b.bill_name,
             b.bill_type,
             b.bill_no,
             b.congress_no,
             r.cycle,
             count(*)::integer as count,
             sum(amount) as amount
         from lobbying_report r
         inner join assoc_lobbying_biggest_client_associations ca using (transaction_id)
         inner join lobbying_issue i using (transaction_id)
         inner join lobbying_bill b on b.issue_id = i.id
         inner join matchbox_entity ce on ce.id = ca.entity_id
         group by ce.name, ca.entity_id, congress_no, bill_id, bill_name, bill_type, bill_no, cycle) ct_amt
        group by client_name, client_entity, congress_no, bill_id, bill_name, bill_type, bill_no, cycle, count, amount
     )
 
     select client_name, client_entity, congress_no, bill_id, bill_name, bill_type, bill_no, cycle, 
        -- title as bill_title, 
        count, amount, rank_by_amount, rank_by_count
    from
(
     select client_name, client_entity, congress_no, bill_id, bill_name, bill_type, bill_no, cycle,  count, amount, rank_by_amount, rank_by_count
     from lobbying_by_cycle lbc
 
     union 
 
     select client_name, client_entity, congress_no, bill_id, bill_name, bill_type, bill_no, -1, count, amount, 
             rank() over (partition by bill_id order by amount desc) as rank_by_amount,
             rank() over (partition by bill_id order by count desc) as rank_by_count
     from (
         select client_name, client_entity, congress_no, bill_id, bill_name, bill_type, bill_no, sum(count) as count, sum(amount) as amount
         from lobbying_by_cycle
         group by client_name, client_entity, congress_no, bill_id, bill_name, bill_type, bill_no
        ) x
    ) a   
--    left join 
--    lobbying_billtitle lbt using (bill_type, bill_no, congress_no)
;
 
 select date_trunc('second', now()) || ' -- create index summary_lobbying_bills_for_biggest_org_idx on summary_lobbying_bills_for_biggest_org (client_entity, cycle)';
 create index summary_lobbying_bills_for_biggest_org_idx on summary_lobbying_bills_for_biggest_org (client_entity, cycle);


