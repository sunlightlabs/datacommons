 -- Ranking Biggest Lobbying Issues for Parentmost Clients by Amount and Count
  
  select date_trunc('second', now()) || ' -- drop table if exists summary_lobbying_issues_for_biggest_org';
  drop table if exists summary_lobbying_top_issues_for_biggest_orgs;
  
  select date_trunc('second', now()) || ' -- create table summary_lobbying_issues_for_biggest_org as';
  create table summary_lobbying_top_issues_for_biggest_orgs as
      with lobbying_by_cycle as (
         select issue, cycle, count, amount,
              rank() over (partition by cycle, issue order by amount desc) as rank_by_amount,
              rank() over (partition by cycle, issue order by count desc) as rank_by_count
         from 
          (select
              i.general_issue as issue,
              r.cycle,
              count(*)::integer as count,
              sum(amount) as amount
          from lobbying_report r
          inner join assoc_lobbying_biggest_client_associations ca using (transaction_id)
          inner join lobbying_issue i using (transaction_id)
          group by i.general_issue, r.cycle) ct_amt
         group by issue, cycle, count, amount
      )
  
      select issue, cycle, count, amount, rank_by_amount, rank_by_count
      from lobbying_by_cycle

      union all
  
      select issue, -1, count, amount, 
              rank() over (partition by issue order by amount desc) as rank_by_amount,
              rank() over (partition by issue order by count desc) as rank_by_count
      from (
          select issue, sum(count) as count, sum(amount) as amount
          from lobbying_by_cycle
          group by issue
      ) x
  ;
  
  select date_trunc('second', now()) || ' -- create index summary_lobbying_issues_for_biggest_org_idx on summary_lobbying_issues_for_biggest_org (client_entity, cycle)';
  create index summary_lobbying_top_issues_for_biggest_orgs_idx on summary_lobbying_top_issues_for_biggest_orgs (issue, cycle, rank_by_amount);

 -- Ranking Biggest Parentmost Clients for Lobbying Issues by Amount and Count
 
  select date_trunc('second', now()) || ' -- drop table if exists summary_lobbying_issues_for_biggest_org';
  drop table if exists summary_lobbying_top_biggest_orgs_for_issue;
  
  select date_trunc('second', now()) || ' -- create table summary_lobbying_issues_for_biggest_org as';
  create table summary_lobbying_top_biggest_orgs_for_issue as
      with lobbying_by_cycle as (
         select client_name, client_entity, cycle, issue, count, amount,
              rank() over (partition by cycle, issue order by amount desc) as rank_by_amount,
              rank() over (partition by cycle, issue order by count desc) as rank_by_count
         from 
          (select
              ce.name as client_name,
              ca.entity_id as client_entity,
              r.cycle,
              i.general_issue as issue,
              count(*)::integer as count,
              sum(amount) as amount
          from lobbying_report r 
          inner join assoc_lobbying_biggest_client_associations ca using (transaction_id)
          inner join lobbying_issue i using (transaction_id)
          inner join matchbox_entity ce on ce.id = ca.entity_id
          group by ce.name, ca.entity_id, r.cycle, i.general_issue) ct_amt
         group by client_name, client_entity, cycle, issue, count, amount
      )
  
      select client_name, client_entity, cycle, issue, count, amount, rank_by_amount, rank_by_count
      from lobbying_by_cycle
  
      union all
  
      select client_name, client_entity, -1, issue, count, amount, 
              rank() over (partition by issue order by amount desc) as rank_by_amount,
              rank() over (partition by issue order by count desc) as rank_by_count
      from (
          select client_name, client_entity, -1, issue, sum(count) as count, sum(amount) as amount
          from lobbying_by_cycle
          group by client_name, client_entity, issue
      ) x
  ;
  
  select date_trunc('second', now()) || ' -- create index summary_lobbying_issues_for_biggest_org_idx on summary_lobbying_issues_for_biggest_org (client_entity, cycle)';
  create index summary_lobbying_top_biggest_orgs_for_issue_idx on summary_lobbying_top_biggest_orgs_for_issue (issue, client_entity, cycle);


 
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


