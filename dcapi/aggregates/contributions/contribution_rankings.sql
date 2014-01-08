
-- CONTRIBUTIONS FROM BIGGEST ORGS BY PARTY


select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_party';
drop table if exists ranked_parentmost_orgs_by_party;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_party';
create table ranked_parentmost_orgs_by_party as

        select
            recipient_party, 
            cycle,
            organization_entity, 
            organization_name, 
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party, cycle order by sum(count) desc) as rank_by_count,
            rank() over(partition by recipient_party, cycle order by sum(amount) desc) as rank_by_amount
        from
        (select
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            aotp.cycle,
            aotp.organization_entity,
            me.name as organization_name,
            count,
            amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_parties aotp on me.id = aotp.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aotp.cycle 
        where
            om.is_org 
            and 
            om.parent_entity_id is null
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id)
            ) three_party
        group by recipient_party, cycle, organization_entity, organization_name;

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_party_cycle_rank_idx ranked_parentmost_orgs_by_party (cycle, rank_by_count)';
create index ranked_parentmost_orgs_by_party_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_party_cycle_rank_idx ranked_parentmost_orgs_by_party (cycle, rank_by_amount)';
create index ranked_parentmost_orgs_by_party_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_party (cycle, rank_by_amount);



-- CONTRIBUTIONS FROM BIGGEST ORGS BY FEDERAL/STATE

select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_state_fed';
drop table if exists ranked_parentmost_orgs_by_state_fed;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_state_fed';
create table ranked_parentmost_orgs_by_state_fed as
        select
            state_or_federal,
            cycle,
            organization_entity,
            me.name as organization_name,
            count,
            amount,
            rank() over(partition by state_or_federal, cycle order by count desc) as rank_by_count,
            rank() over(partition by state_or_federal, cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_state_fed aosf on me.id = aosf.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = aosf.organization_entity and om.cycle = asof.cycle 
        where
            om.is_org 
            and
            om.parent_entity_id is null 
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id)
;

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_state_fed_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_state_fed (cycle, rank_by_count)';
create index ranked_parentmost_orgs_by_state_fed_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_state_fed (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_state_fed_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_state_fed (cycle, rank_by_amount)';
create index ranked_parentmost_orgs_by_state_fed_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_state_fed (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM BIGGEST ORGS BY SEAT

select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_office_type';
drop table if exists ranked_parentmost_orgs_by_seat;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_office_type';
create table ranked_parentmost_orgs_by_seat as
        select
            seat,
            cycle,
            organization_entity,
            me.name,
            count,
            amount,
            rank() over(partition by seat, cycle order by count desc) as rank_by_count,
            rank() over(partition by seat, cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_seat aots on me.id = aots.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle 
        where
            om.is_org 
            and
            om.parent_id is null 
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_office_type_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_office_type_org (cycle, rank_by_count)';
create index ranked_parentmost_orgs_by_office_type_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_office_type (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_office_type_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_office_type_org (cycle, rank_by_amount)';
create index ranked_parentmost_orgs_by_office_type_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_office_type (cycle, rank_by_amount);

-- CONTRIBTUIONS FROM BIGGEST ORGS, BROKEN OUT BY SOURCE (ASSOC'D INDIVS OR PACS)

select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_indiv_pac';
drop table if exists ranked_parentmost_orgs_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_indiv_pac';
create table ranked_parentmost_orgs_by_indiv_pac as
    select
        cycle, 
        me.name as organization_name,
        organization_entity, 
        (pacs_count + indivs_count) as total_count,
        (pacs_amount + indivs_amount) as total_amount,
        pacs_count,
        pacs_amount, 
        indivs_count, 
        indivs_amount,
        rank() over(partition by cycle order by total_count desc)   as total_count,
        rank() over(partition by cycle order by total_amount desc)  as total_amount,
        rank() over(partition by cycle order by pacs_count desc)    as rank_by_pacs_count,
        rank() over(partition by cycle order by pacs_amount desc)   as rank_by_pacs_amount,
        rank() over(partition by cycle order by indivs_count desc)  as rank_by_indivs_count,
        rank() over(partition by cycle order by indivs_amount desc) as rank_by_indivs_amount
        from
            aggregate_organizations_by_indiv_pac aoip
                inner join
            matchbox_entity me on me.id = aoip.organization_entity
                inner join 
            matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aoip.cycle 
        where
            om.is_org 
            and 
            om.parent_id is null;

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_total_amount_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_total_amount)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_total_amount_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_total_amount);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_total_count_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_total_count)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_total_count_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_total_count);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_pacs_amount_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_pacs_amount)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_pacs_amount_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_pacs_amount);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_pacs_count_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_pacs_count)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_pacs_count_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_pacs_count);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_indivs_amount_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_indivs_amount)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_indivs_amount_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_indivs_amount);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_indivs_count_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_indivs_count)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_indivs_count_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_indivs_count);


-- CONTRIBUTIONS FROM INDIVIDUALS BY PARTY

select date_trunc('second', now()) || ' -- drop table if exists ranked_individuals_by_party';
drop table if exists ranked_individuals_by_party;

select date_trunc('second', now()) || ' -- create table ranked_individuals_by_party';
create table ranked_individuals_by_party as

        select
            recipient_party, 
            cycle,
            individual_entity, 
            individual_name, 
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party,cycle order by sum(count) desc) as rank_by_count,
            rank() over(partition by recipient_party,cycle order by sum(amount) desc) as rank_by_amount
        from
        (
        select
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            cycle,
            individual_entity,
            me.name as individual_name,
            count,
            amount
        from
                matchbox_entity me
            inner join
                aggregate_individual_to_parties aitp on me.id = aitp.individual_entity
             -- maybe filter out lobbyists
             -- inner join
             --  matchbox_individualmetadata mim on mim.entity_id = me.id
             -- where not mim.is_lobbyist
            ) three_party
        group by recipient_part, cycle, individual_entity, individual_name
        ;

select date_trunc('second', now()) || ' -- create index ranked_individuals_by_party_cycle_rank_by_count_idx on ranked_individuals_by_party (cycle, rank_by_count)';
create index ranked_individuals_by_party_idx on ranked_individuals_by_party (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_individuals_by_party_cycle_rank_by_amount_idx on ranked_individuals_by_party (cycle, rank_by_amount)';
create index ranked_individuals_by_party_idx on ranked_individuals_by_party (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM INDIVIDUALS BY FEDERAL/STATE

 select date_trunc('second', now()) || ' -- drop table if exists ranked_individuals_by_state_fed';
 drop table if exists ranked_individuals_by_state_fed;

 select date_trunc('second', now()) || ' -- create table ranked_individuals_by_state_fed';
 create table ranked_individuals_by_state_fed as
         select
             state_fed,
             cycle,
             individual_entity,
             me.name as individual_name,
             count,
             amount,
             rank() over(partition by state_fed, cycle order by count desc) as rank_by_count,
             rank() over(partition by state_fed, cycle order by amount desc) as rank_by_amount
         from
                 matchbox_entity me
             inner join
                 aggregate_individual_to_state_fed aisf on me.id = aisf.individual_entity
             -- maybe filter out lobbyists
             -- inner join
             --  matchbox_individualmetadata mim on mim.entity_id = me.id
             -- where not mim.is_lobbyist
   ;

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_state_fed_cycle_rank_by_count_idx on ranked_individuals_by_state_fed (cycle, rank_by_count)';
 create index ranked_individuals_by_state_fed_cycle_rank_by_count_idx on ranked_individuals_by_state_fed (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_state_fed_cycle_rank_by_amount_idx on ranked_individuals_by_state_fed (cycle, rank_by_amount)';
 create index ranked_individuals_by_state_fed_cycle_rank_by_amount_idx on ranked_individuals_by_state_fed (cycle, rank_by_amount);

 -- CONTRIBUTIONS FROM INDIVIDUALS BY SEAT

 select date_trunc('second', now()) || ' -- drop table if exists ranked_individuals_by_seat';
 drop table if exists ranked_individuals_by_seat;

 select date_trunc('second', now()) || ' -- create table ranked_individuals_by_seat';
 create table ranked_individuals_by_seat as
         select
             seat,
             cycle,
             individual_entity,
             me.name as individual_name,
             count,
             amount,
             rank() over(partition by seat, cycle order by count desc) as rank_by_count,
             rank() over(partition by seat, cycle order by amount desc) as rank_by_amount
         from
                 matchbox_entity me
             inner join
                 aggregate_individual_to_seat ais on me.id = ais.individual_entity
             -- maybe filter out lobbyists
             -- inner join
             --  matchbox_individualmetadata mim on mim.entity_id = me.id
             -- where not mim.is_lobbyist
   ;

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_seat_cycle_rank_by_count_idx on ranked_individuals_by_seat (cycle, rank_by_count)';
 create index ranked_individuals_by_seat_cycle_rank_by_count_idx on ranked_individuals_by_seat (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_seat_cycle_rank_by_amount_idx on ranked_individuals_by_seat (cycle, rank_by_amount)';
 create index ranked_individuals_by_seat_cycle_rank_by_amount_idx on ranked_individuals_by_seat (cycle, rank_by_amount);

 -- CONTRIBUTIONS FROM INDIVIDUALS BY GROUP/POLITICIAN

 select date_trunc('second', now()) || ' -- drop table if exists ranked_individuals_by_recipient_type';
 drop table if exists ranked_individuals_by_recipient_type;

 select date_trunc('second', now()) || ' -- create table ranked_individuals_by_recipient_type';
 create table ranked_individuals_by_recipient_type as
         select
             recipient_type,
             cycle,
             individual_entity,
             me.name as individual_name,
             count,
             amount,
             rank() over(partition by recipient_type, cycle order by count desc) as rank_by_count,
             rank() over(partition by recipient_type, cycle order by amount desc) as rank_by_amount
         from
                 matchbox_entity me
             inner join
                 aggregate_individual_to_recipient_types airt on me.id = airt.individual_entity
             -- maybe filter out lobbyists
             -- inner join
             --  matchbox_individualmetadata mim on mim.entity_id = me.id
             -- where not mim.is_lobbyist
   ;

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_recipient_type_cycle_rank_by_count_idx on ranked_individuals_by_recipient_type (cycle, rank_by_count)';
 create index ranked_individuals_by_recipient_type_cycle_rank_by_count_idx on ranked_individuals_by_recipient_type (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_recipient_type_cycle_rank_by_amount_idx on ranked_individuals_by_recipient_type (cycle, rank_by_amount)';
 create index ranked_individuals_by_recipient_type_cycle_rank_by_amount_idx on ranked_individuals_by_recipient_type (cycle, rank_by_amount);


 -- CONTRIBUTIONS FROM INDIVIDUALS BY IN-STATE/OUT-OF-STATE

 select date_trunc('second', now()) || ' -- drop table if exists ranked_individuals_by_in_state_out_of_state';
 drop table if exists ranked_individuals_by_in_state_out_of_state;

 select date_trunc('second', now()) || ' -- create table ranked_individuals_by_in_state_out_of_state';
 create table ranked_individuals_by_in_state_out_of_state as
         select
             in_state_out_of_state,
             cycle,
             individual_entity,
             me.name as individual_name,
             count,
             amount,
             rank() over(partition by in_state_out_of_state, cycle order by count desc) as rank_by_count,
             rank() over(partition by in_state_out_of_state, cycle order by amount desc) as rank_by_amount
         from
                 matchbox_entity me
             inner join
                 aggregate_individual_to_in_state_out_of_state ais on me.id = ais.individual_entity
             -- maybe filter out lobbyists
             -- inner join
             --  matchbox_individualmetadata mim on mim.entity_id = me.id
             -- where not mim.is_lobbyist
   ;

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_count)';
 create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_amount)';
 create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_amount);



-- CONTRIBUTIONS FROM LOBBYISTS BY PARTY

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_party';
drop table if exists ranked_lobbyists_by_party cascade;

select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_party';
create table ranked_lobbyists_by_party as

        select
            recipient_party, 
            cycle,
            lobbyist_entity, 
            lobbyist_name, 
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party,cycle order by sum(count) desc) as rank_by_count,
            rank() over(partition by recipient_party,cycle order by sum(amount) desc) as rank_by_amount
        from
        (
        select
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            cycle,
            individual_entity as lobbiyst_entity,
            me.name as lobbyist_name,
            count,
            amount
        from
            matchbox_entity me
                inner join
            aggregate_individual_to_parties aitp on me.id = aitp.lobbyist_entity
                inner join
            matchbox_lobbyistmetadata mim on mim.entity_id = me.id
         where mim.is_lobbyist
            ) three_party
        group by recipient_party, cycle, lobbyist_entity, lobbyist_name
        ;

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_party_cycle_rank_by_count_idx on ranked_lobbyists_by_party (cycle, rank_by_count)';
create index ranked_lobbyists_by_party_idx on ranked_lobbyists_by_party (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_party_cycle_rank_by_amount_idx on ranked_lobbyists_by_party (cycle, rank_by_amount)';
create index ranked_lobbyists_by_party_idx on ranked_lobbyists_by_party (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM LOBBYISTS BY FEDERAL/STATE
 
select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_state_fed';
drop table if exists ranked_lobbyists_by_state_fed cascade;

select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_state_fed';
create table ranked_lobbyists_by_state_fed as
        select
            state_fed,
            cycle,
            individual_entity as lobbyist_entity,
            me.name as individual_name as lobbyist_name,
            count,
            amount,
            rank() over(partition by state_fed, cycle order by count desc) as rank_by_count,
            rank() over(partition by state_fed, cycle order by amount desc) as rank_by_amount
        from
            matchbox_entity me
                inner join
            aggregate_individual_to_state_fed aisf on me.id = aisf.individual_entity
                inner join
            matchbox_individualmetadata mim on mim.entity_id = me.id
        where mim.is_lobbyist
  ;

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_state_fed_cycle_rank_by_count_idx on ranked_lobbyists_by_state_fed (cycle, rank_by_count)';
create index ranked_lobbyists_by_state_fed_cycle_rank_by_count_idx on ranked_lobbyists_by_state_fed (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_state_fed_cycle_rank_by_amount_idx on ranked_lobbyists_by_state_fed (cycle, rank_by_amount)';
create index ranked_lobbyists_by_state_fed_cycle_rank_by_amount_idx on ranked_lobbyists_by_state_fed (cycle, rank_by_amount);



 -- CONTRIBUTIONS FROM LOBBYISTS BY SEAT
 
select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_seat';
 drop table if exists ranked_lobbyists_by_seat;

 select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_seat';
 create table ranked_lobbyists_by_seat as
         select
             seat,
             cycle,
             individual_entity as lobbyist_entity,
             me.name as individual_name as lobbyist_name,
             count,
             amount,
             rank() over(partition by seat, cycle order by count desc) as rank_by_count,
             rank() over(partition by seat, cycle order by amount desc) as rank_by_amount
         from
             matchbox_entity me
                inner join
             aggregate_individual_to_seat ais on me.id = ais.individual_entity
                inner join
             matchbox_individualmetadata mim on mim.entity_id = me.id
         where mim.is_lobbyist
   ;

 select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_seat_cycle_rank_by_count_idx on ranked_lobbyists_by_seat (cycle, rank_by_count)';
 create index ranked_lobbyists_by_seat_cycle_rank_by_count_idx on ranked_lobbyists_by_seat (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_seat_cycle_rank_by_amount_idx on ranked_lobbyists_by_seat (cycle, rank_by_amount)';
 create index ranked_lobbyists_by_seat_cycle_rank_by_amount_idx on ranked_lobbyists_by_seat (cycle, rank_by_amount);
 
-- CONTRIBUTIONS FROM LOBBYISTS BY GROUP/POLITICIAN

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_recipient_type';
drop table if exists ranked_lobbyists_by_recipient_type;

select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_recipient_type';
create table ranked_lobbyists_by_recipient_type as
        select
            recipient_type,
            cycle,
            individual_entity as lobbyist_entity,
            me.name as lobbyist_name,
            count,
            amount,
            rank() over(partition by recipient_type, cycle order by count desc) as rank_by_count,
            rank() over(partition by recipient_type, cycle order by amount desc) as rank_by_amount
        from
            matchbox_entity me
                inner join
            aggregate_individual_to_recipient_types airt on me.id = airt.individual_entity
                inner join
            matchbox_individualmetadata mim on mim.entity_id = me.id
         where mim.is_lobbyist
  ;

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_recipient_type_cycle_rank_by_count_idx on ranked_lobbyists_by_recipient_type (cycle, rank_by_count)';
create index ranked_lobbyists_by_recipient_type_cycle_rank_by_count_idx on ranked_lobbyists_by_recipient_type (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_recipient_type_cycle_rank_by_amount_idx on ranked_lobbyists_by_recipient_type (cycle, rank_by_amount)';
create index ranked_lobbyists_by_recipient_type_cycle_rank_by_amount_idx on ranked_lobbyists_by_recipient_type (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM LOBBYISTS BY IN-STATE/OUT-OF-STATE

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_in_state_out_of_state';
drop table if exists ranked_lobbyists_by_in_state_out_of_state;

select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_in_state_out_of_state';
create table ranked_lobbyists_by_in_state_out_of_state as
        select
            in_state_out_of_state,
            cycle,
            individual_entity as lobbyist_entity,
            me.name as individual_name as lobbyist_name,
            count,
            amount,
            rank() over(partition by in_state_out_of_state, cycle order by count desc) as rank_by_count,
            rank() over(partition by in_state_out_of_state, cycle order by amount desc) as rank_by_amount
        from
            matchbox_entity me
                inner join
            aggregate_individual_to_in_state_out_of_state ais on me.id = ais.individual_entity
                inner join
            matchbox_individualmetadata mim on mim.entity_id = me.id
         where mim.is_lobbyist
  ;

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_count)';
create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_amount)';
create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM LOBBYING ORGS BY PARTY


select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_party';
drop table if exists ranked_lobbying_orgs_by_party;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_party';
create table ranked_lobbying_orgs_by_party as

        select
            recipient_party, 
            cycle,
            lobbying_firm_entity, 
            lobbying_firm_name, 
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party, cycle order by sum(count) desc) as rank_by_count,
            rank() over(partition by recipient_party, cycle order by sum(amount) desc) as rank_by_amount
        from
        (select
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            aotp.cycle,
            aotp.organization_entity as lobbying_firm_entity,
            me.name as organization_name as lobbying_firm_name,
            count,
            amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_parties aotp on me.id = aotp.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = me.id  and om.cycle = aotp.cycle 
        where
            om.lobbying_firm
            ) three_party
        group by recipient_party, cycle, organization_entity, organization_name;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_party_cycle_rank_idx ranked_lobbying_orgs_by_party (cycle, rank_by_count)';
create index ranked_lobbying_orgs_by_party_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_party_cycle_rank_idx ranked_lobbying_orgs_by_party (cycle, rank_by_amount)';
create index ranked_lobbying_orgs_by_party_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_party (cycle, rank_by_amount);



-- CONTRIBUTIONS FROM LOBBYING ORGS BY FEDERAL/STATE

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_state_fed';
drop table if exists ranked_lobbying_orgs_by_state_fed;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_state_fed';
create table ranked_lobbying_orgs_by_state_fed as
        select
            state_or_federal,
            cycle,
            organization_entity as lobbying_firm_entity,
            me.name as lobbying_firm_name,
            count,
            amount,
            rank() over(partition by state_or_federal, cycle order by count desc) as rank_by_count,
            rank() over(partition by state_or_federal, cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_state_fed aosf on me.id = aosf.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = aosf.organization_entity and om.cycle = asof.cycle 
        where
            om.lobbying_firm
;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_count)';
create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_amount)';
create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM LOBBYING ORGS BY SEAT

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_office_type';
drop table if exists ranked_lobbying_orgs_by_seat;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_office_type';
create table ranked_lobbying_orgs_by_seat as
        select
            seat,
            cycle,
            organization_entity as lobbying_firm_entity,
            me.name as lobbying_firm_name,
            count,
            amount,
            rank() over(partition by seat, cycle order by count desc) as rank_by_count,
            rank() over(partition by seat, cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_seat aots on me.id = aots.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = me.id  and om.cycle = aots.cycle 
        where
            om.lobbying_firm
;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_office_type_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_office_type_org (cycle, rank_by_count)';
create index ranked_lobbying_orgs_by_office_type_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_office_type (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_office_type_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_office_type_org (cycle, rank_by_amount)';
create index ranked_lobbying_orgs_by_office_type_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_office_type (cycle, rank_by_amount);

-- CONTRIBTUIONS FROM LOBBYING ORGS, BROKEN OUT BY SOURCE (ASSOC'D INDIVS OR PACS)

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_indiv_pac';
drop table if exists ranked_lobbying_orgs_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_indiv_pac';
create table ranked_lobbying_orgs_by_indiv_pac as
    select
        cycle, 
        me.name as lobbying_firm_name,
        organization_entity as lobbying_firm_entity, 
        (pacs_count + indivs_count) as total_count,
        (pacs_amount + indivs_amount) as total_amount,
        pacs_count,
        pacs_amount, 
        indivs_count, 
        indivs_amount,
        rank() over(partition by cycle order by total_count desc)   as total_count,
        rank() over(partition by cycle order by total_amount desc)  as total_amount,
        rank() over(partition by cycle order by pacs_count desc)    as rank_by_pacs_count,
        rank() over(partition by cycle order by pacs_amount desc)   as rank_by_pacs_amount,
        rank() over(partition by cycle order by indivs_count desc)  as rank_by_indivs_count,
        rank() over(partition by cycle order by indivs_amount desc) as rank_by_indivs_amount
        from
            aggregate_organizations_by_indiv_pac aoip
                inner join
            matchbox_entity me on me.id = aoip.organization_entity
                inner join 
            matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aoip.cycle 
        where
            om.lobbying_firm;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_total_amount_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_total_amount)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_total_amount_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_total_amount);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_total_count_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_total_count)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_total_count_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_total_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_pacs_amount_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_pacs_amount)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_pacs_amount_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_pacs_amount);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_pacs_count_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_pacs_count)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_pacs_count_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_pacs_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_indivs_amount_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_indivs_amount)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_indivs_amount_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_indivs_amount);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_indivs_count_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_indivs_count)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_indivs_count_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_indivs_count);


-- CONTRIBUTIONS FROM BIGGEST POL GROUPS BY PARTY


select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_party';
drop table if exists ranked_pol_groups_by_party;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_party';
create table ranked_pol_groups_by_party as

        select
            recipient_party, 
            cycle,
            organization_entity, 
            organization_name, 
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party, cycle order by sum(count) desc) as rank_by_count,
            rank() over(partition by recipient_party, cycle order by sum(amount) desc) as rank_by_amount
        from
        (select
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            aotp.cycle,
            aotp.organization_entity,
            me.name as organization_name,
            count,
            amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_parties aotp on me.id = aotp.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle 
        where
            om.is_pol_group 
            and 
            om.parent_entity_id is null
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id)
            ) three_party
        group by recipient_party, cycle, organization_entity, organization_name;

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_party_cycle_rank_idx ranked_pol_groups_by_party (cycle, rank_by_count)';
create index ranked_pol_groups_by_party_cycle_rank_by_count_idx on ranked_pol_groups_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_party_cycle_rank_idx ranked_pol_groups_by_party (cycle, rank_by_amount)';
create index ranked_pol_groups_by_party_cycle_rank_by_amount_idx on ranked_pol_groups_by_party (cycle, rank_by_amount);



-- CONTRIBUTIONS FROM BIGGEST POL GROUPS BY FEDERAL/STATE

select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_state_fed';
drop table if exists ranked_pol_groups_by_state_fed;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_state_fed';
create table ranked_pol_groups_by_state_fed as
        select
            state_or_federal,
            cycle,
            organization_entity,
            me.name as organization_name,
            count,
            amount,
            rank() over(partition by state_or_federal, cycle order by count desc) as rank_by_count,
            rank() over(partition by state_or_federal, cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_state_fed aosf on me.id = aosf.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = aosf.organization_entity and om.cycle = asof.cycle 
        where
            om.is_pol_group 
            and
            om.parent_entity_id is null 
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id)
;

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_state_fed_cycle_rank_by_count_idx on ranked_pol_groups_by_state_fed (cycle, rank_by_count)';
create index ranked_pol_groups_by_state_fed_cycle_rank_by_count_idx on ranked_pol_groups_by_state_fed (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_state_fed_cycle_rank_by_amount_idx on ranked_pol_groups_by_state_fed (cycle, rank_by_amount)';
create index ranked_pol_groups_by_state_fed_cycle_rank_by_amount_idx on ranked_pol_groups_by_state_fed (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM BIGGEST POL GROUPS BY SEAT

select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_office_type';
drop table if exists ranked_pol_groups_by_seat;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_office_type';
create table ranked_pol_groups_by_seat as
        select
            seat,
            cycle,
            organization_entity,
            me.name,
            count,
            amount,
            rank() over(partition by seat, cycle order by count desc) as rank_by_count,
            rank() over(partition by seat, cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_seat aots on me.id = aots.organization_entity
            inner join 
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle 
        where
            om.is_pol_group 
            and
            om.parent_id is null 
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_office_type_cycle_rank_by_count_idx on ranked_pol_groups_by_office_type_org (cycle, rank_by_count)';
create index ranked_pol_groups_by_office_type_cycle_rank_by_count_idx on ranked_pol_groups_by_office_type (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_office_type_cycle_rank_by_amount_idx on ranked_pol_groups_by_office_type_org (cycle, rank_by_amount)';
create index ranked_pol_groups_by_office_type_cycle_rank_by_amount_idx on ranked_pol_groups_by_office_type (cycle, rank_by_amount);

-- CONTRIBTUIONS FROM BIGGEST POL GROUPS, BROKEN OUT BY SOURCE (ASSOC'D INDIVS OR PACS)

select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_indiv_pac';
drop table if exists ranked_pol_groups_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_indiv_pac';
create table ranked_pol_groups_by_indiv_pac as
    select
        cycle, 
        me.name as organization_name,
        organization_entity, 
        (pacs_count + indivs_count) as total_count,
        (pacs_amount + indivs_amount) as total_amount,
        pacs_count,
        pacs_amount, 
        indivs_count, 
        indivs_amount,
        rank() over(partition by cycle order by total_count desc)   as total_count,
        rank() over(partition by cycle order by total_amount desc)  as total_amount,
        rank() over(partition by cycle order by pacs_count desc)    as rank_by_pacs_count,
        rank() over(partition by cycle order by pacs_amount desc)   as rank_by_pacs_amount,
        rank() over(partition by cycle order by indivs_count desc)  as rank_by_indivs_count,
        rank() over(partition by cycle order by indivs_amount desc) as rank_by_indivs_amount
        from
            aggregate_organizations_by_indiv_pac aoip
                inner join
            matchbox_entity me on me.id = aoip.organization_entity
                inner join 
            matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aoip.cycle 
        where
            om.is_pol_group 
            and 
            om.parent_id is null;

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_total_amount_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_total_amount)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_total_amount_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_total_amount);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_total_count_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_total_count)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_total_count_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_total_count);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_pacs_amount_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_pacs_amount)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_pacs_amount_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_pacs_amount);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_pacs_count_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_pacs_count)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_pacs_count_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_pacs_count);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_indivs_amount_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_indivs_amount)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_indivs_amount_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_indivs_amount);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_indivs_count_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_indivs_count)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_indivs_count_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_indivs_count);

