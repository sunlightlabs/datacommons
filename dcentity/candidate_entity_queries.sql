select recipient_name, transaction_namespace, recipient_ext_id, max(cycle)
from contribution_contribution
where recipient_type = 'P'
group by recipient_name, transaction_namespace, recipient_ext_id
order by max(cycle) desc;



select r1.recipient_name, r1.transaction_namespace, r1.recipient_ext_id, r2.recipient_ext_id
    from tmp_recipients r1
    inner join tmp_recipients r2 
        on r1.recipient_name = r2.recipient_name and r1.transaction_namespace = r2.transaction_namespace
    where length(r1.recipient_ext_id) > 0 and length(r2.recipient_ext_id) > 0
        and r1.recipient_ext_id != r2.recipient_ext_id;
        
        
        
create table tmp_ided_recipients as        
select min(recipient_name), transaction_namespace, recipient_ext_id, max(cycle)
from contribution_contribution
where 
    recipient_type = 'P'
    and recipient_ext_id != ''
group by transaction_namespace, recipient_ext_id
order by max(cycle) desc;


create table tmp_unided_recipients as
select recipient_name, transaction_namespace, recipient_state, max(cycle)
from contribution_contribution
where 
    recipient_type = 'P'
    and recipient_ext_id = ''
group by recipient_name, transaction_namespace, recipient_state
order by max(cycle) desc;


create table tmp_ided_organizations as
select orgs.organization_name, orgs.transaction_namespace, orgs.organization_ext_id, max(orgs.max)
from
(select organization_name, transaction_namespace, organization_ext_id, max(cycle)
from contribution_contribution
where organization_name != '' and organization_ext_id != ''
group by organization_name, transaction_namespace, organization_ext_id
union
select parent_organization_name, transaction_namespace, parent_organization_ext_id, max(cycle)
from contribution_contribution
where parent_organization_name != '' and parent_organization_ext_id != ''
group by parent_organization_name, transaction_namespace, parent_organization_ext_id) as orgs
group by organization_name, transaction_namespace, organization_ext_id
order by max(orgs.max);

select count(*) 
from contribution_contribution c1
inner join contribution_contribution c2
    on c1.recipient_name = c2.recipient_name
where c1.recipient_state != c2.recipient_state;


select * from contribution_contribution o
where 
    o.cycle = '2010'
and
    exists (select * from contribution_contribution i
                where o.recipient_name = i.recipient_name
                and o.recipient_state != i.recipient_state);
                
                
                
                
update contribution_contribution
set contributor_name = trim(both ' ' from contributor_name)
where contributor_name like ' %' or contributor_name like '% ';
update contribution_contribution
set contributor_employer = trim(both ' ' from contributor_employer)
where contributor_employer like ' %' or contributor_employer like '% ';
update contribution_contribution
set organization_name = trim(both ' ' from organization_name)
where organization_name like ' %' or organization_name like '% ';
update contribution_contribution
set parent_organization_name = trim(both ' ' from parent_organization_name)
where parent_organization_name like ' %' or parent_organization_name like '% ';
update contribution_contribution
set committee_name = trim(both ' ' from committee_name)
where committee_name like ' %' or committee_name like '% ';
update contribution_contribution
set recipient_name = trim(both ' ' from recipient_name)
where recipient_name like ' %' or recipient_name like '% ';


                