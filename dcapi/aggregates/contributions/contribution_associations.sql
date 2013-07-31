
-- Cycles: controls the cycles for which aggregates are computed
-- Mainly of using during development, when it helps to be able to regenerate the aggregates quickly.

select date_trunc('second', now()) || ' -- Starting contribution associations...';

select date_trunc('second', now()) || ' -- drop table if exists agg_cycles cascade';
drop table if exists agg_cycles cascade;

select date_trunc('second', now()) || ' -- create table agg_cycles';
create table agg_cycles as
    -- values (2005), (2006), (2007), (2008), (2009), (2010);
    select distinct cycle from contribution_contribution;

drop table if exists agg_suppressed_catcodes cascade;
create table agg_suppressed_catcodes as values
    ('Z0000'), ('Z1000'), ('Z1100'), ('Z1200'), ('Z1300'), ('Z1400'),
    ('Z2100'), ('Z2200'), ('Z2300'), ('Z2400'),
    ('Z4100'), ('Z4200'), ('Z4300'),
    ('Z5000'), ('Z5100'), ('Z5200'), ('Z5300'),
    ('Z7777'),
    ('Z8888'),
    ('Z9100'), ('Z9500'), ('Z9600'), ('Z9700'), ('Z9800'), ('Z9999');


-- this table was created by hand reviewing all orgnames that appear more than 200 times

drop table if exists agg_suppressed_orgnames cascade;
create table agg_suppressed_orgnames as values
    ('retired'), ('homemaker'), ('attorney'), ('[24i contribution]'), ('self-employed'), ('physician'),
    ('self'), ('information requested'), ('self employed'), ('[24t contribution]'), ('consultant'), ('investor'),
    ('[candidate contribution]'), ('n/a'), ('farmer'), ('real estate'), ('none'), ('writer'),
    ('dentist'), ('info requested'), ('business owner'), ('accountant'), ('artist'), ('rancher'),
    ('student'), ('realtor'), ('investments'), ('real estate developer'), ('unemployed'), ('requested'),
    ('owner'), ('developer'), ('businessman'), ('contractor'), ('president'), ('engineer'),
    ('n'), ('psychologist'), ('real estate broker'), ('executive'), ('private investor'), ('architect'),
    ('sales'), ('real estate investor'), ('selfemployed'), ('philanthropist'), ('not employed'), ('author'),
    ('builder'), ('insurance agent'), ('volunteer'), ('construction'), ('insurance'), ('entrepreneur'),
    ('lobbyist'), ('ceo'), ('n.a'), ('actor'), ('photographer'), ('musician'),
    ('interior designer'), ('restaurant owner'), ('teacher'), ('designer'), ('surgeon'), ('social worker'),
    ('veterinarian'), ('psychiatrist'), ('chiropractor'), ('auto dealer'), ('small business owner'), ('optometrist'),
    ('producer'), ('business'), ('.information requested'), ('financial advisor'), ('pharmacist'), ('psychotherapist'),
    ('manager'), ('management consultant'), ('general contractor'), ('finance'), ('orthodontist'), ('actress'),
    ('n.a.'), ('restauranteur'), ('property management'), ('home builder'), ('oil & gas'), ('real estate investments'),
    ('geologist'), ('professor'), ('farming'), ('real estate agent'), ('na'), ('financial planner'),
    ('community volunteer'), ('property manager'), ('political consultant'), ('public relations'), ('business consultant'), ('publisher'),
    ('insurance broker'), ('educator'), ('nurse'), ('orthopedic surgeon'), ('editor'), ('marketing'),
    ('dairy farmer'), ('investment advisor'), ('freelance writer'), ('investment banker'), ('trader'), ('computer consultant'),
    ('banker'), ('oral surgeon'), ('business executive'), ('unknown'), ('civic volunteer'), ('filmmaker'),
    ('economist'), ('');



-- Adjust the odd-year cycles upward


select date_trunc('second', now()) || ' -- drop view if exists contributions_even_cycles cascade';
drop view if exists contributions_even_cycles cascade;

select date_trunc('second', now()) || ' -- create view contributions_even_cycles';
create view contributions_even_cycles as
    select transaction_id, transaction_namespace, transaction_type, amount,
        case when cycle % 2 = 0 then cycle else cycle + 1 end as cycle, date,
        contributor_name, contributor_ext_id, contributor_type, contributor_category, contributor_occupation, contributor_state, contributor_zipcode,
        organization_name, organization_ext_id, parent_organization_name, parent_organization_ext_id,
        recipient_name, recipient_ext_id, recipient_type, recipient_party, recipient_state, recipient_category, seat
    from contribution_contribution;



-- Only contributions that should be included in totals from individuals to politicians

select date_trunc('second', now()) || ' -- drop table if exists contributions_individual';
drop table if exists contributions_individual;

select date_trunc('second', now()) || ' -- create table contributions_individual';
create table contributions_individual as
    select *
    from contributions_even_cycles c
    where
        (c.contributor_type is null or c.contributor_type in ('', 'I'))
        and c.recipient_type = 'P'
        and c.transaction_type in ('', '10', '11', '15', '15e', '15j', '22y')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and c.recipient_category not like 'Z4%'
        and cycle in (select * from agg_cycles);

select date_trunc('second', now()) || ' -- create index contributions_individual_transaction_id on contributions_individual (transaction_id)';
create index contributions_individual_transaction_id on contributions_individual (transaction_id);


-- Only contributions from individuals to organizations

select date_trunc('second', now()) || ' -- drop table if exists contributions_individual_to_organization';
drop table if exists contributions_individual_to_organization cascade;

select date_trunc('second', now()) || ' -- create table contributions_individual_to_organization';
create table contributions_individual_to_organization as
    select *
    from contributions_even_cycles c
    where
        (c.contributor_type is null or c.contributor_type in ('', 'I'))
        and c.recipient_type = 'C'
        and c.transaction_type in ('', '10', '11', '15', '15e', '15j', '22y')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and c.recipient_category not like 'Z4%'
        and cycle in (select * from agg_cycles);

select date_trunc('second', now()) || ' -- create index contributions_individual_to_organization_transaction_id on contributions_individual_to_organization (transaction_id)';
create index contributions_individual_to_organization_transaction_id on contributions_individual_to_organization (transaction_id);


-- Organization contributions to candidates

select date_trunc('second', now()) || ' -- drop table if exists contributions_organization';
drop table if exists contributions_organization cascade;

select date_trunc('second', now()) || ' -- create table contributions_organization';
create table contributions_organization as
    select *
    from contributions_even_cycles c
    where
        contributor_type = 'C'
        and recipient_type = 'P'
        and transaction_type in ('', '24k', '24r', '24z')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and c.recipient_category not like 'Z4%'
        and cycle in (select * from agg_cycles);

select date_trunc('second', now()) || ' -- create index contributions_organization_transaction_id on contributions_organization (transaction_id)';
create index contributions_organization_transaction_id on contributions_organization (transaction_id);


-- Organization contributions to PACs

select date_trunc('second', now()) || ' -- drop table if exists contributions_org_to_pac';
drop table if exists contributions_org_to_pac cascade;

select date_trunc('second', now()) || ' -- create table contributions_org_to_pac';
create table contributions_org_to_pac as
    select *
    from contributions_even_cycles c
    where
        contributor_type = 'C'
        and recipient_type = 'C'
        and transaction_type in ('', '24k', '24r', '24z')
        and c.contributor_category not in (select * from agg_suppressed_catcodes)
        and c.recipient_category not like 'Z4%'
        and cycle in (select * from agg_cycles);

select date_trunc('second', now()) || ' -- create index contributions_org_to_pac_transaction_id on contributions_org_to_pac (transaction_id)';
create index contributions_org_to_pac_transaction_id on contributions_org_to_pac (transaction_id);


-- All contributions that we can aggregate. Partitioned by transaction_namespace.

select date_trunc('second', now()) || ' -- drop table if exists contributions_all_relevant';
drop table if exists contributions_all_relevant cascade;

select date_trunc('second', now()) || ' -- create table contributions_all_relevant';
create table contributions_all_relevant as select * from contributions_even_cycles limit 0;

create table contributions_all_relevant__crp ( check ( transaction_namespace = 'urn:fec:transaction' ) ) inherits (contributions_all_relevant);
create table contributions_all_relevant__nimsp ( check ( transaction_namespace = 'urn:nimsp:transaction' ) ) inherits (contributions_all_relevant);

insert into contributions_all_relevant__crp
    select * from (
        table contributions_individual
        union all
        table contributions_individual_to_organization
        union all
        table contributions_organization
        union all
        table contributions_org_to_pac
    ) x
    where transaction_namespace = 'urn:fec:transaction'
;
insert into contributions_all_relevant__nimsp
    select * from (
        table contributions_individual
        union all
        table contributions_individual_to_organization
        union all
        table contributions_organization
        union all
        table contributions_org_to_pac
    ) x
    where transaction_namespace = 'urn:nimsp:transaction'
;

select date_trunc('second', now()) || ' -- create index contributions_all_relevant__transaction_id__idx on contributions_all_relevant (transaction_id)';
create index contributions_all_relevant__transaction_id__idx on contributions_all_relevant (transaction_id);


-- Contributor Associations

select date_trunc('second', now()) || ' -- drop table if exists tmp_assoc_indiv_id';
drop table if exists tmp_assoc_indiv_id cascade;

select date_trunc('second', now()) || ' -- create table tmp_assoc_indiv_id (with crp transactions)';
create table tmp_assoc_indiv_id as
    -- Not sure the CTE is totally necessary here, but it does have the effect of pushing the nested loop farther down the explain tree,
    -- and away from the very top, where it was before. The estimated cost was a little bit higher, but execution time seemed to be far quicker.
    -- It may have helped Postgres make better estimates and a better plan.
    with indiv_c as (select transaction_id, contributor_ext_id from contributions_all_relevant__crp where contributor_type = 'I')
    select entity_id, transaction_id
    from indiv_c c
    inner join matchbox_entityattribute a
        on (a.value = c.contributor_ext_id
                    -- a 12th digit of '0' can be ignored
                    or (length(a.value) = 12 and substring(a.value from 12 for 1) = '0' and substring(a.value for 11) = c.contributor_ext_id))
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        e.type = 'individual'
        and a.value != ''
        and a.namespace = 'urn:crp:individual'
;

select date_trunc('second', now()) || ' -- insert into tmp_assoc_indiv_id (nimsp transactions)';
insert into tmp_assoc_indiv_id (entity_id, transaction_id)
    with indiv_c as (select transaction_id, contributor_ext_id from contributions_all_relevant__nimsp where contributor_type is null or contributor_type != 'C')
    select entity_id, transaction_id
    from indiv_c c
    inner join matchbox_entityattribute a
        on a.value = c.contributor_ext_id
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        e.type = 'individual'
        and a.value != ''
        and a.namespace = 'urn:nimsp:individual'
;
create index tmp_assoc_indiv_id_entity on tmp_assoc_indiv_id (entity_id);
create index tmp_assoc_indiv_id_transaction on tmp_assoc_indiv_id (transaction_id);


drop table if exists tmp_indiv_names cascade;

select date_trunc('second', now()) || ' -- create table tmp_indiv_names';
create table tmp_indiv_names as
    select entity_id, contributor_name as name
    from contributions_all_relevant c
    inner join tmp_assoc_indiv_id a using (transaction_id)
    group by entity_id, contributor_name;

create index tmp_indiv_names_entity on tmp_indiv_names (entity_id);
create index tmp_indiv_names_name on tmp_indiv_names (lower(name));


drop table if exists tmp_indiv_locations cascade;

select date_trunc('second', now()) || ' -- create table tmp_indiv_locations';
create table tmp_indiv_locations as
    select entity_id, msa_id
    from contributions_all_relevant c
    inner join tmp_assoc_indiv_id a using (transaction_id)
    inner join geo_zip on c.contributor_zipcode = zipcode
    group by entity_id, msa_id;

create index tmp_indiv_locations_entity on tmp_indiv_locations (entity_id);


select date_trunc('second', now()) || ' -- drop table if exists contributor_associations';
drop table if exists contributor_associations cascade;

select date_trunc('second', now()) || ' -- create table contributor_associations';
create table contributor_associations as
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join matchbox_entityalias a
        on lower(c.contributor_name) = lower(a.alias)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        e.type = 'organization'
        and ((a.namespace = '' or a.namespace is null)
            or ((a.namespace like 'urn:crp:%' and c.transaction_namespace = 'urn:fec:transaction')
                or (a.namespace like 'urn:nimsp:%' and c.transaction_namespace = 'urn:nimsp:transaction')))
union
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join matchbox_entityattribute a
        on c.contributor_ext_id = a.value and a.value != ''
    where
        c.contributor_type = 'C'
        and (
            (a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction' )
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction')
        )
union
    select * from tmp_assoc_indiv_id
union
    select n.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join tmp_indiv_names n
        on lower(n.name) = lower(c.contributor_name)
    inner join tmp_indiv_locations l
        on n.entity_id = l.entity_id
    inner join geo_zip z
        on c.contributor_zipcode = z.zipcode and l.msa_id = z.msa_id
    group by n.entity_id, c.transaction_id;


select date_trunc('second', now()) || ' -- create index contributor_associations_entity_id on contributor_associations (entity_id)';
create index contributor_associations_entity_id on contributor_associations (entity_id);
select date_trunc('second', now()) || ' -- create index contributor_associations_transaction_id on contributor_associations (transaction_id)';
create index contributor_associations_transaction_id on contributor_associations (transaction_id);


-- Organization Associations

select date_trunc('second', now()) || ' -- drop table if exists organization_associations';
drop table if exists organization_associations cascade;

select date_trunc('second', now()) || ' -- create table organization_associations';
create table organization_associations as
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join matchbox_entityalias a
        on lower(c.organization_name) = lower(a.alias)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        e.type = 'organization'
        and ((a.namespace = '' or a.namespace is null)
            or ((a.namespace like 'urn:crp:%' and c.transaction_namespace = 'urn:fec:transaction')
                or (a.namespace like 'urn:nimsp:%' and c.transaction_namespace = 'urn:nimsp:transaction')))
union
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join matchbox_entityattribute a
        on c.organization_ext_id = a.value and a.value != ''
    where
        (a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
            or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction');

select date_trunc('second', now()) || ' -- create index organization_associations_entity_id on organization_associations (entity_id)';
create index organization_associations_entity_id on organization_associations (entity_id);
select date_trunc('second', now()) || ' -- create index organization_associations_transaction_id on organization_associations (transaction_id)';
create index organization_associations_transaction_id on organization_associations (transaction_id);


-- Parent Organization Associations

select date_trunc('second', now()) || ' -- drop table if exists parent_organization_associations';
drop table if exists parent_organization_associations cascade;

select date_trunc('second', now()) || ' -- create table parent_organization_associations';
    create table parent_organization_associations as
        select a.entity_id, c.transaction_id
            from contributions_all_relevant c
            inner join matchbox_entityalias a
                on lower(c.parent_organization_name) = lower(a.alias)
            inner join matchbox_entity e
                on e.id = a.entity_id
            where
                e.type = 'organization'
                and ((a.namespace = '' or a.namespace is null)
                    or ((a.namespace like 'urn:crp:%' and c.transaction_namespace = 'urn:fec:transaction')
                        or (a.namespace like 'run:nimsp:%' and c.transaction_namespace = 'urn:nimsp:transaction')))
    union
        select a.entity_id, c.transaction_id
        from contributions_all_relevant c
        inner join matchbox_entityattribute a
            on c.parent_organization_ext_id = a.value and a.value != ''
        where
            (a.namespace = 'urn:crp:organization' and c.transaction_namespace = 'urn:fec:transaction')
                or (a.namespace = 'urn:nimsp:organization' and c.transaction_namespace = 'urn:nimsp:transaction');

select date_trunc('second', now()) || ' -- create index parent_organization_associations_entity_id on parent_organization_associations (entity_id)';
create index parent_organization_associations_entity_id on parent_organization_associations (entity_id);
select date_trunc('second', now()) || ' -- create index parent_organization_associations_transaction_id on parent_organization_associations (transaction_id)';
create index parent_organization_associations_transaction_id on parent_organization_associations (transaction_id);


-- "Biggest" Organiztion Associations
-- preferences parent org when present, otherwise org

select date_trunc('second', now()) || ' -- drop table if exists biggest_organization_associations';
drop table if exists biggest_organization_associations cascade;

select date_trunc('second', now()) || ' -- create table biggest_organization_associations';
create table biggest_organization_associations as
    select coalesce(pa.entity_id, oa.entity_id) as entity_id, transaction_id
    from organization_associations oa
    full outer join parent_organization_associations pa using (transaction_id);

select date_trunc('second', now()) || ' -- create index biggest_organization_associations_entity_id on biggest_organization_associations (entity_id)';
create index biggest_organization_associations_entity_id on biggest_organization_associations (entity_id);
select date_trunc('second', now()) || ' -- create index biggest_organization_associations_transaction_id on biggest_organization_associations (transaction_id)';
create index biggest_organization_associations_transaction_id on biggest_organization_associations (transaction_id);


-- Industry Associations

select date_trunc('second', now()) || ' -- drop table if exists industry_associations';
drop table if exists industry_associations cascade;

select date_trunc('second', now()) || ' -- create table industry_associations';
create table industry_associations as
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join agg_cat_map cm
        on lower(c.contributor_category) = lower(cm.catcode)
    inner join matchbox_entityattribute a
        on lower(cm.catorder) = lower(a.value)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        e.type = 'industry'
union all
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join matchbox_entityattribute a
        on lower(c.contributor_category) = lower(a.value)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        e.type = 'industry';

select date_trunc('second', now()) || ' -- create index industry_associations_entity_id on industry_associations (entity_id)';
create index industry_associations_entity_id on industry_associations (entity_id);
select date_trunc('second', now()) || ' -- create index industry_associations_transaction_id on industry_associations (transaction_id)';
create index industry_associations_transaction_id on industry_associations (transaction_id);


-- Recipient Associations

select date_trunc('second', now()) || ' -- drop table if exists recipient_associations';
drop table if exists recipient_associations cascade;

select date_trunc('second', now()) || ' -- create table recipient_associations';
create table recipient_associations as
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join matchbox_entityalias a
        on lower(c.recipient_name) = lower(a.alias)
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        e.type = 'organization' -- name matching only for organizations; politicians should all have IDs
        and ((a.namespace = '' or a.namespace is null)
            or ((a.namespace like 'urn:crp:%' and c.transaction_namespace = 'urn:fec:transaction')
                or (a.namespace like 'run:nimsp:%' and c.transaction_namespace = 'urn:nimsp:transaction')))
union
    select a.entity_id, c.transaction_id
    from contributions_all_relevant c
    inner join matchbox_entityattribute a
        on c.recipient_ext_id = a.value and a.value != ''
    inner join matchbox_entity e
        on e.id = a.entity_id
    where
        (a.namespace = 'urn:crp:recipient' and c.transaction_namespace = 'urn:fec:transaction' and c.recipient_type = 'P')
            or (a.namespace = 'urn:nimsp:recipient' and c.transaction_namespace = 'urn:nimsp:transaction' and c.recipient_type = 'P');


select date_trunc('second', now()) || ' -- create index recipient_associations_entity_id on recipient_associations (entity_id)';
create index recipient_associations_entity_id on recipient_associations (entity_id);
select date_trunc('second', now()) || ' -- create index recipient_associations_transaction_id on recipient_associations (transaction_id)';
create index recipient_associations_transaction_id on recipient_associations (transaction_id);


-- Flattened contributions with all associations included. Not aggregated. (save for industries)
select date_trunc('second', now()) || ' -- drop table if exists contributions_flat';
drop table if exists contributions_flat;
select date_trunc('second', now()) || ' -- create table contributions_flat';
create table contributions_flat as
    select
        transaction_id,
        transaction_namespace,

        contributor_name,
        ca.entity_id as contributor_entity,
        contributor_type,

        organization_name,
        oa.entity_id as organization_entity,

        parent_organization_name,
        poa.entity_id as parent_organization_entity,

        recipient_name,
        ra.entity_id as recipient_entity,
        recipient_type,
        recipient_party as party,
        seat,

        cycle,
        amount
    from contributions_all_relevant
    left join contributor_associations ca using (transaction_id)
    left join organization_associations oa using (transaction_id)
    left join parent_organization_associations poa using (transaction_id)
    left join recipient_associations ra using (transaction_id)
;

select date_trunc('second', now()) || ' -- create index contributions_flat__contributor_type_idx';
create index contributions_flat__contributor_type_idx on contributions_flat (contributor_type);
select date_trunc('second', now()) || ' -- create index contributions_flat__recipient_type_idx';
create index contributions_flat__recipient_type_idx on contributions_flat (recipient_type);
select date_trunc('second', now()) || ' -- create index contributions_flat__cycle_idx';
create index contributions_flat__cycle_idx on contributions_flat (cycle);

select date_trunc('second', now()) || ' -- finished contribution associations';
