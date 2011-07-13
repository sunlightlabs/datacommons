

drop table if exists tmp_lobbying_value;
create table tmp_lobbying_value as
    select transaction_id, amount / count(*) as value
    from lobbying_report
    inner join lobbying_issue using (transaction_id)
    inner join lobbying_lobbyist using (transaction_id)
    where
        amount > 0
    group by transaction_id, amount;

drop table if exists tmp_lobbyist_issue;
create table tmp_lobbyist_issue as
    select lobbyist_ext_id, general_issue_code, sum(value) as value
    from lobbying_lobbyist
    inner join lobbying_issue using (transaction_id)
    inner join tmp_lobbying_value using (transaction_id)
    group by lobbyist_ext_id, general_issue_code;
    
drop table if exists tmp_lobbyist_total;
create table tmp_lobbyist_total as    
    select lobbyist_ext_id, sum(value) as total
    from tmp_lobbyist_issue
    group by lobbyist_ext_id;
    
drop table if exists tmp_lobbyist_specialization;
create table tmp_lobbyist_specialization as
    select lobbyist_ext_id, sum(value ^ 2) / total ^ 2 as specialization, sum(value ^ 2) / total ^ 2 <= .25 as generalist, sum(value ^ 2) / total ^ 2 >= .75 as specialist
    from tmp_lobbyist_issue
    inner join tmp_lobbyist_total using (lobbyist_ext_id)
    group by lobbyist_ext_id, total;
    

drop table if exists tmp_lobbyist_specialist_issues;
create table tmp_lobbyist_specialist_issues as
    select distinct on (lobbyist_ext_id) lobbyist_ext_id, general_issue_code as issue
    from tmp_lobbyist_issue
    inner join tmp_lobbyist_specialization using (lobbyist_ext_id)
    where
        specialist
    order by lobbyist_ext_id, value desc;

create table tmp_issue_descriptions as
    select general_issue_code as issue, general_issue as description
    from lobbying_issue
    group by general_issue_code, general_issue;

select description, count(*)
from tmp_lobbyist_specialist_issues 
inner join tmp_issue_descriptions using (issue)
group by description
order by count(*) desc
limit 10;



select catorder, avg(case when specialist then 1.0 else 0.0 end) as portion_specialized
from lobbying_report
inner join agg_cat_map on catcode = client_category
inner join lobbying_lobbyist using (transaction_id)
inner join tmp_lobbyist_specialization using (lobbyist_ext_id)
group by catorder
order by avg(case when specialist then 1.0 else 0.0 end)
limit 10;
    
select substring(catorder for 1), avg(case when specialist then 1.0 else 0.0 end) as portion_specialized
from lobbying_report
inner join agg_cat_map on catcode = client_category
inner join lobbying_lobbyist using (transaction_id)
inner join tmp_lobbyist_specialization using (lobbyist_ext_id)
group by substring(catorder for 1)
order by avg(case when specialist then 1.0 else 0.0 end) desc;


create table tmp_lobbyist_categories as
    select lobbyist_ext_id, client_category as category
    from lobbying_lobbyist
    inner join lobbying_lobbying using (transaction_id)
    group by lobbyist_ext_id, client_category;

select count(*)
from tmp_lobbyist_categories
where
    category = 'C5120';

select bucket, count(*)::float / (select count(*) from tmp_lobbyist_specialization) as 
from tmp_lobbyist_specialization
cross join (values (0.0), (0.1), (0.2), (0.3), (0.4), (0.5), (0.6), (0.7), (0.8), (0.9)) h (bucket)
--inner join tmp_lobbyist_categories using (lobbyist_ext_id)
where
    specialization > bucket
    and specialization <= bucket + 0.1
    --and category = 'C5120'
group by bucket
order by bucket;


