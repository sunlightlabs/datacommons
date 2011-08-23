\set agg_top_n 10

DROP FUNCTION IF EXISTS standardize_orgname(text);
CREATE FUNCTION standardize_orgname(text) RETURNS text AS $$
    select regexp_replace(lower($1), E'( ?co\\.?$)|( ?corp\\.?$)|( ?corporation$)|( ?company$)|( ?inc\\.?$)|( ?incorporated$)|( ?assoc\\.?$)|( ?association$)|( ?ltd\\.?$)|( ?limited$)|( ?llc\\.?$)', '', 'g') as result;
$$ LANGUAGE SQL;


-- Grants View

drop view if exists grants_record;

create view grants_record as
    select id, recipient_name,
        case when fiscal_year % 2 = 0 then fiscal_year else fiscal_year + 1 end as cycle,
        case when asst_cat_type in ('l', 'i') then 'l' else 'g' end as spending_type,
        fiscal_year, agency_name, project_description as description, 
        case when asst_cat_type in ('l', 'i') then face_loan_guran else fed_funding_amount end as amount
    from grants_grant;


-- Contracts View

drop view if exists contracts_record;

create view contracts_record as
    select c.id, vendorname as recipient_name,
            case when fiscal_year % 2 = 0 then fiscal_year else fiscal_year + 1 end as cycle,
            fiscal_year, coalesce(a.name, '') as agency_name, descriptionofcontractrequirement as description, obligatedamount as amount
    from contracts_contract c
    left join contracts_agencies a on agencyid = a.id;


-- Grant Associations

drop table if exists assoc_spending_grants;

create table assoc_spending_grants as
    select e.id as entity_id, g.id as transaction_id
    from grants_grant g
    inner join matchbox_entityalias a on
        standardize_orgname(g.recipient_name) = standardize_orgname(a.alias)
    inner join matchbox_entity e on e.id = a.entity_id
    where
        e.type = 'organization'
    group by e.id, g.id;

create index assoc_spending_grants_entity_id on assoc_spending_grants (entity_id);
create index assoc_spending_grants_transaction_id on assoc_spending_grants (transaction_id);


-- Contract Associations

drop table if exists assoc_spending_contracts;

create table assoc_spending_contracts as
    select e.id as entity_id, c.id as transaction_id
    from contracts_contract c
    inner join matchbox_entityalias a on
        standardize_orgname(c.vendorname) = standardize_orgname(a.alias)
    inner join matchbox_entity e on e.id = a.entity_id
    where
        e.type = 'organization'
    group by e.id, c.id;
    
create index assoc_spending_contracts_entity_id on assoc_spending_contracts (entity_id);
create index assoc_spending_contracts_transaction_id on assoc_spending_contracts (transaction_id);


-- Spending Totals

drop table if exists agg_spending_totals;

create table agg_spending_totals as
    with totals_by_cycle as (
        select recipient_entity, cycle,
                coalesce(grants.count, 0) as grant_count, 
                coalesce(grants.amount, 0) as grant_amount,
                coalesce(contracts.count, 0) as contract_count, 
                coalesce(contracts.amount, 0) as contract_amount,
                coalesce(loans.count, 0) as loan_count, 
                coalesce(loans.amount, 0) as loan_amount
        from (
            select entity_id as recipient_entity, cycle, count(*), sum(amount) as amount
            from grants_record
            inner join assoc_spending_grants on (id = transaction_id)
            where
                spending_type = 'g'
            group by entity_id, cycle) as grants
        full outer join (
            select entity_id as recipient_entity, cycle, count(*), sum(amount) as amount
            from grants_record
            inner join assoc_spending_grants on (id = transaction_id)
            where
                spending_type = 'l'
            group by entity_id, cycle) as loans
        using (recipient_entity, cycle)
        full outer join (
            select entity_id as recipient_entity, cycle, count(*), sum(amount) as amount
            from contracts_record
            inner join assoc_spending_contracts on (id = transaction_id)
            group by entity_id, cycle) as contracts
        using (recipient_entity, cycle)
    )

    select * from totals_by_cycle

    union all

    select recipient_entity, -1,
            sum(grant_count) as grant_count, sum(grant_amount) as grant_amount,
            sum(contract_count) as contract_count, sum(contract_amount) as contract_amount,
            sum(loan_count) as loan_count, sum(loan_amount) as loan_amount
    from totals_by_cycle
    group by recipient_entity;

create index agg_spending_totals_idx on agg_spending_totals (recipient_entity);


-- Top Grants & Contracts

drop table if exists agg_spending_org;

create table agg_spending_org as
    with spending_to_org as (
        select entity_id as recipient_entity, recipient_name, spending_type,
                cycle, fiscal_year, agency_name, description, amount
        from grants_record
        inner join assoc_spending_grants on (id = transaction_id)

        union all

        select entity_id as recipient_entity, recipient_name, 'c' as spending_type,
                cycle, fiscal_year, agency_name, description, amount
        from contracts_record
        inner join assoc_spending_contracts on (id = transaction_id)
    )

    select recipient_entity, recipient_name, spending_type, cycle, fiscal_year, agency_name, description, amount
    from (select *, rank() over (partition by recipient_entity, cycle order by amount desc) as rank from spending_to_org) x
    where rank <= :agg_top_n

    union all

    select recipient_entity, recipient_name, spending_type, -1 as cycle, fiscal_year, agency_name, description, amount
    from (select *, rank() over (partition by recipient_entity order by amount desc) as rank from spending_to_org) x
    where rank <= :agg_top_n;

create index agg_spending_org_idx on agg_spending_org (recipient_entity, cycle);

