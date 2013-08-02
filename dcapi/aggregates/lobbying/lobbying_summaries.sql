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

  select date_trunc('second', now()) || ' -- create index summary_lobbying_top_biggest_orgs_for_top_issues_idx on summary_lobbying_top_biggest_orgs_for_top_issues (cycle, issue_rank_by_amount)';
  create index summary_lobbying_top_biggest_orgs_for_top_issues_cycle_issue_rank_idx on summary_lobbying_top_biggest_orgs_for_top_issues (cycle, issue_rank_by_amount);

  select date_trunc('second', now()) || ' -- create index summary_lobbying_top_biggest_orgs_for_top_issues_idx on summary_lobbying_top_biggest_orgs_for_top_issues (cycle, client_rank_by_amount)';
  create index summary_lobbying_top_biggest_orgs_for_top_issues_cycle_client_rank_idx on summary_lobbying_top_biggest_orgs_for_top_issues (cycle, client_rank_by_amount);

-- Top 10 Parentmost Clients for Top 10 Lobbied Bills by Amount

  select date_trunc('second', now()) || ' -- drop table if exists summary_lobbying_top_biggest_orgs_for_top_bills';
  drop table if exists summary_lobbying_top_biggest_orgs_for_top_bills;
  
  select date_trunc('second', now()) || ' -- create table summary_lobbying_top_biggest_orgs_for_top_bills';
  create table summary_lobbying_top_biggest_orgs_for_top_bills as
       select lb.cycle, lb.congress_no, lb.bill_type, lb.bill_no, me.name, bo.client_entity as id, bo.count as client_count, bo.rank_by_count as client_rank_by_count, bo.amount as client_amount, bo.rank_by_amount as client_rank_by_amount, lb.count as bill_total_count, lb.rank_by_count as bill_rank_by_count, lb.amount as bill_total_amount, lb.rank_by_amount as bill_rank_by_amount
        from 
            agg_lobbying_bills_across_biggest_orgs lb
          inner join
            agg_lobbying_biggest_orgs_for_bills bo on 
                    bo.congress_no =  lb.congress_no
                and bo.bill_type = lb.bill_type
                and bo.bill_no = lb.bill_no
                and bo.cycle = lb.cycle
          inner join
            matchbox_entity me on me.id = bo.client_entity
        where bo.rank_by_amount <= 10 and lb.rank_by_amount <= 10
        order by cycle, bill_rank_by_amount, client_rank_by_amount;

  select date_trunc('second', now()) || ' -- create index summary_lobbying_top_biggest_orgs_for_top_bills_idx on summary_lobbying_top_biggest_orgs_for_top_bills (cycle, bill_rank_by_amount)';
  create index summary_lobbying_top_biggest_orgs_for_top_bills_cycle_bill_rank_idx on summary_lobbying_top_biggest_orgs_for_top_bills (cycle, bill_rank_by_amount);

  select date_trunc('second', now()) || ' -- create index summary_lobbying_top_biggest_orgs_for_top_bills_idx on summary_lobbying_top_biggest_orgs_for_top_bills (cycle, client_rank_by_amount)';
  create index summary_lobbying_top_biggest_orgs_for_top_bills_cycle_client_rank_idx on summary_lobbying_top_biggest_orgs_for_top_bills (cycle, client_rank_by_amount);

