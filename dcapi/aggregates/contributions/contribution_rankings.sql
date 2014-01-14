
-- CONTRIBUTIONS FROM BIGGEST ORGS BY PARTY
-- SELECT 66584
-- Time: 1819.086 ms
-- CREATE INDEX
-- Time: 161.574 ms
-- CREATE INDEX
-- Time: 131.900 ms


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
            (recipient_party is not null and recipient_party != '')
            and
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
-- SELECT 40103
-- Time: 1316.740 ms
-- CREATE INDEX
-- Time: 91.265 ms
-- CREATE INDEX
-- Time: 84.947 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_state_fed';
drop table if exists ranked_parentmost_orgs_by_state_fed;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_state_fed';
create table ranked_parentmost_orgs_by_state_fed as
        select
            state_or_federal,
            aosf.cycle,
            aosf.organization_entity,
            me.name as organization_name,
            count,
            amount,
            rank() over(partition by state_or_federal, aosf.cycle order by count desc) as rank_by_count,
            rank() over(partition by state_or_federal, aosf.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_state_fed aosf on me.id = aosf.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = aosf.organization_entity and om.cycle = aosf.cycle
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
-- SELECT 120765
-- Time: 4725.656 ms
-- CREATE INDEX
-- Time: 257.808 ms
-- CREATE INDEX
-- Time: 257.808 msi

select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_seat';
drop table if exists ranked_parentmost_orgs_by_seat;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_seat';
create table ranked_parentmost_orgs_by_seat as
        select
            seat,
            om.cycle,
            organization_entity,
            me.name as organization_name,
            count,
            amount,
            rank() over(partition by seat, om.cycle order by count desc) as rank_by_count,
            rank() over(partition by seat, om.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_seat aots on me.id = aots.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle
        where
            (seat is not null and seat != '')
            and
            om.is_org
            and
            om.parent_entity_id is null
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_seat_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_seat_org (cycle, rank_by_count)';
create index ranked_parentmost_orgs_by_seat_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_seat (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_seat_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_seat_org (cycle, rank_by_amount)';
create index ranked_parentmost_orgs_by_seat_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_seat (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM BIGGEST ORGS BY recipient_type
-- SELECT 51049
-- Time: 1400.675 ms
-- CREATE INDEX
-- Time: 114.063 ms
-- CREATE INDEX
-- Time: 149.312 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_recipient_type';
drop table if exists ranked_parentmost_orgs_by_recipient_type;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_recipient_type';
create table ranked_parentmost_orgs_by_recipient_type as
        select
            recipient_type,
            om.cycle,
            organization_entity,
            me.name as organization_name,
            count,
            amount,
            rank() over(partition by recipient_type, om.cycle order by count desc) as rank_by_count,
            rank() over(partition by recipient_type, om.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_recipient_type aots on me.id = aots.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle
        where
            (recipient_type is not null and recipient_type != '')
            and
            om.is_org
            and
            om.parent_entity_id is null
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_recipient_type_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_recipient_type_org (cycle, rank_by_count)';
create index ranked_parentmost_orgs_by_recipient_type_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_recipient_type (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_recipient_type_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_recipient_type_org (cycle, rank_by_amount)';
create index ranked_parentmost_orgs_by_recipient_type_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_recipient_type (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM BIGGEST ORGS BY INDIV/PAC
-- SELECT 57616
-- Time: 1628.601 ms
-- CREATE INDEX
-- Time: 123.874 ms
-- CREATE INDEX
-- Time: 120.520 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_parentmost_orgs_by_indiv_pac';
drop table if exists ranked_parentmost_orgs_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table ranked_parentmost_orgs_by_indiv_pac';
create table ranked_parentmost_orgs_by_indiv_pac as
        select
            direct_or_indiv,
            om.cycle,
            organization_entity,
            me.name as organization_name,
            count,
            amount,
            rank() over(partition by direct_or_indiv, om.cycle order by count desc) as rank_by_count,
            rank() over(partition by direct_or_indiv, om.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_by_indiv_pac aots on me.id = aots.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle
        where
            (direct_or_indiv is not null and direct_or_indiv != '')
            and
            om.is_org
            and
            om.parent_entity_id is null
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_indiv_pac_org (cycle, rank_by_count)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_count_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_indiv_pac_org (cycle, rank_by_amount)';
create index ranked_parentmost_orgs_by_indiv_pac_cycle_rank_by_amount_idx on ranked_parentmost_orgs_by_indiv_pac (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM INDIVIDUALS BY PARTY
-- SELECT 156890
-- Time: 2854.962 ms
-- CREATE INDEX
-- Time: 334.013 ms
-- CREATE INDEX
-- Time: 337.589 ms

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
        where    
            (recipient_party is not null and recipient_party != '')
            ) three_party
        group by recipient_party, cycle, individual_entity, individual_name
        ;

select date_trunc('second', now()) || ' -- create index ranked_individuals_by_party_cycle_rank_by_count_idx on ranked_individuals_by_party (cycle, rank_by_count)';
create index ranked_individuals_by_party_cycle_count_idx on ranked_individuals_by_party (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_individuals_by_party_cycle_rank_by_amount_idx on ranked_individuals_by_party (cycle, rank_by_amount)';
create index ranked_individuals_by_party_cycle_amount_idx on ranked_individuals_by_party (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM INDIVIDUALS BY FEDERAL/STATE
-- SELECT 130140
-- Time: 4303.812 ms
-- CREATE INDEX
-- Time: 272.283 ms
-- CREATE INDEX
-- Time: 274.684 ms

 select date_trunc('second', now()) || ' -- drop table if exists ranked_individuals_by_state_fed';
 drop table if exists ranked_individuals_by_state_fed;

 select date_trunc('second', now()) || ' -- create table ranked_individuals_by_state_fed';
 create table ranked_individuals_by_state_fed as
         select
             state_or_federal,
             cycle,
             individual_entity,
             me.name as individual_name,
             count,
             amount,
             rank() over(partition by state_or_federal, cycle order by count desc) as rank_by_count,
             rank() over(partition by state_or_federal, cycle order by amount desc) as rank_by_amount
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
-- SELECT 279285
-- Time: 6952.617 ms
-- CREATE INDEX
-- Time: 623.251 ms
-- CREATE INDEX
-- Time: 688.030 ms

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
        where
            (seat is not null and seat != '')
   ;

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_seat_cycle_rank_by_count_idx on ranked_individuals_by_seat (cycle, rank_by_count)';
 create index ranked_individuals_by_seat_cycle_rank_by_count_idx on ranked_individuals_by_seat (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_seat_cycle_rank_by_amount_idx on ranked_individuals_by_seat (cycle, rank_by_amount)';
 create index ranked_individuals_by_seat_cycle_rank_by_amount_idx on ranked_individuals_by_seat (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM INDIVIDUALS BY GROUP/POLITICIAN
-- SELECT 145440
-- Time: 2223.772 ms
-- CREATE INDEX
-- Time: 298.492 ms
-- CREATE INDEX
-- Time: 292.258 ms

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
-- SELECT 118951
-- Time: 3298.045 ms
-- CREATE INDEX
-- Time: 239.777 ms
-- CREATE INDEX
-- Time: 246.164 ms


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
                 aggregate_individual_by_in_state_out_of_state ais on me.id = ais.individual_entity
             -- maybe filter out lobbyists
             -- inner join
             --  matchbox_individualmetadata mim on mim.entity_id = me.id
             -- where not mim.is_lobbyist
        where    
            (in_state_out_of_state is not null and in_state_out_of_state != '')
   ;

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_count)';
 create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_amount)';
 create index ranked_individuals_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_individuals_by_in_state_out_of_state (cycle, rank_by_amount);



-- CONTRIBUTIONS FROM LOBBYISTS BY PARTY
-- SELECT 84066
-- Time: 1520.428 ms
-- CREATE INDEX
-- Time: 184.446 ms
-- CREATE INDEX
-- Time: 167.973 ms

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
            aitp.cycle,
            individual_entity as lobbyist_entity,
            me.name as lobbyist_name,
            count,
            amount
        from
            matchbox_entity me
                inner join
            aggregate_individual_to_parties aitp on me.id = aitp.individual_entity
                inner join
            matchbox_individualmetadata mim on mim.entity_id = me.id
         where 
            mim.is_lobbyist
                and
            (recipient_party is not null and recipient_party != '')
        ) three_party
        group by recipient_party, cycle, lobbyist_entity, lobbyist_name
        ;

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_party_cycle_rank_by_count_idx on ranked_lobbyists_by_party (cycle, rank_by_count)';
create index ranked_lobbyists_by_party_count_idx on ranked_lobbyists_by_party (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_party_cycle_rank_by_amount_idx on ranked_lobbyists_by_party (cycle, rank_by_amount)';
create index ranked_lobbyists_by_party_amount_idx on ranked_lobbyists_by_party (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM LOBBYISTS BY FEDERAL/STATE
-- SELECT 68998
-- Time: 1518.865 ms
-- CREATE INDEX
-- Time: 136.638 ms
-- CREATE INDEX
-- Time: 142.167 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_state_fed';
drop table if exists ranked_lobbyists_by_state_fed cascade;

select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_state_fed';
create table ranked_lobbyists_by_state_fed as
        select
            state_or_federal,
            aisf.cycle,
            individual_entity as lobbyist_entity,
            me.name as lobbyist_name,
            count,
            amount,
            rank() over(partition by state_or_federal, cycle order by count desc) as rank_by_count,
            rank() over(partition by state_or_federal, cycle order by amount desc) as rank_by_amount
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
-- SELECT 147456
-- Time: 3658.465 ms
-- CREATE INDEX
-- Time: 310.077 ms
-- CREATE INDEX
-- Time: 295.290 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_seat';
 drop table if exists ranked_lobbyists_by_seat;

 select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_seat';
 create table ranked_lobbyists_by_seat as
         select
             seat,
             cycle,
             individual_entity as lobbyist_entity,
             me.name as lobbyist_name,
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
         where 
            mim.is_lobbyist
                and    
            (seat is not null and seat != '')
   ;

 select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_seat_cycle_rank_by_count_idx on ranked_lobbyists_by_seat (cycle, rank_by_count)';
 create index ranked_lobbyists_by_seat_cycle_rank_by_count_idx on ranked_lobbyists_by_seat (cycle, rank_by_count);

 select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_seat_cycle_rank_by_amount_idx on ranked_lobbyists_by_seat (cycle, rank_by_amount)';
 create index ranked_lobbyists_by_seat_cycle_rank_by_amount_idx on ranked_lobbyists_by_seat (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM LOBBYISTS BY GROUP/POLITICIAN
-- SELECT 77445
-- Time: 1187.250 ms
-- CREATE INDEX
-- Time: 152.960 ms
-- CREATE INDEX
-- Time: 159.314 ms

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
-- SELECT 61677
-- Time: 1785.575 ms
-- CREATE INDEX
-- Time: 121.845 ms
-- CREATE INDEX
-- Time: 118.950 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbyists_by_in_state_out_of_state';
drop table if exists ranked_lobbyists_by_in_state_out_of_state;

select date_trunc('second', now()) || ' -- create table ranked_lobbyists_by_in_state_out_of_state';
create table ranked_lobbyists_by_in_state_out_of_state as
        select
            in_state_out_of_state,
            cycle,
            individual_entity as lobbyist_entity,
            me.name as lobbyist_name,
            count,
            amount,
            rank() over(partition by in_state_out_of_state, cycle order by count desc) as rank_by_count,
            rank() over(partition by in_state_out_of_state, cycle order by amount desc) as rank_by_amount
        from
            matchbox_entity me
                inner join
            aggregate_individual_by_in_state_out_of_state ais on me.id = ais.individual_entity
                inner join
            matchbox_individualmetadata mim on mim.entity_id = me.id
        where 
            mim.is_lobbyist
                and    
            (in_state_out_of_state is not null and in_state_out_of_state != '')
  ;

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_count)';
create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_count_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_amount)';
create index ranked_lobbyists_by_in_state_out_of_state_cycle_rank_by_amount_idx on ranked_lobbyists_by_in_state_out_of_state (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM LOBBYING ORGS BY PARTY
-- SELECT 19072
-- Time: 574.869 ms
-- CREATE INDEX
-- Time: 56.587 ms
-- CREATE INDEX
-- Time: 58.595 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_party';
drop table if exists ranked_lobbying_orgs_by_party;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_party';
create table ranked_lobbying_orgs_by_party as

        select
            recipient_party,
            cycle,
            lobbying_org_entity,
            lobbying_org_name,
            sum(count) as count,
            sum(amount) as amount,
            rank() over(partition by recipient_party, cycle order by sum(count) desc) as rank_by_count,
            rank() over(partition by recipient_party, cycle order by sum(amount) desc) as rank_by_amount
        from
        (select
            case when recipient_party in ('D','R') then recipient_party else 'Other' end as recipient_party,
            aotp.cycle,
            aotp.organization_entity as lobbying_org_entity,
            me.name as lobbying_org_name,
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
                and
            om.parent_entity_id is null
                and    
            (recipient_party is not null and recipient_party != '')
            ) three_party
        group by recipient_party, cycle, lobbying_org_entity, lobbying_org_name;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_party_cycle_rank_idx ranked_lobbying_orgs_by_party (cycle, rank_by_count)';
create index ranked_lobbying_orgs_by_party_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_party_cycle_rank_idx ranked_lobbying_orgs_by_party (cycle, rank_by_amount)';
create index ranked_lobbying_orgs_by_party_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_party (cycle, rank_by_amount);



-- CONTRIBUTIONS FROM LOBBYING ORGS BY FEDERAL/STATE
-- SELECT 13415
-- Time: 543.707 ms
-- CREATE INDEX
-- Time: 30.131 ms
-- CREATE INDEX
-- Time: 32.187 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_state_fed';
drop table if exists ranked_lobbying_orgs_by_state_fed;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_state_fed';
create table ranked_lobbying_orgs_by_state_fed as
        select
            state_or_federal,
            aosf.cycle,
            aosf.organization_entity as lobbying_org_entity,
            me.name as lobbying_org_name,
            count,
            amount,
            rank() over(partition by state_or_federal, aosf.cycle order by count desc) as rank_by_count,
            rank() over(partition by state_or_federal, aosf.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_state_fed aosf on me.id = aosf.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = aosf.organization_entity and om.cycle = aosf.cycle
        where
            om.lobbying_firm
                and
            om.parent_entity_id is null
;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_count)';
create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_amount)';
create index ranked_lobbying_orgs_by_state_fed_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_state_fed (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM LOBBYING ORGS BY SEAT
-- SELECT 35619
-- Time: 1317.012 ms
-- CREATE INDEX
-- Time: 75.123 ms
-- CREATE INDEX
-- Time: 71.920 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_seat';
drop table if exists ranked_lobbying_orgs_by_seat;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_seat';
create table ranked_lobbying_orgs_by_seat as
        select
            aots.seat,
            aots.cycle,
            organization_entity as lobbying_org_entity,
            me.name as lobbying_org_name,
            count,
            amount,
            rank() over(partition by aots.seat, aots.cycle order by count desc) as rank_by_count,
            rank() over(partition by aots.seat, aots.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_seat aots on me.id = aots.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = me.id  and om.cycle = aots.cycle
        where
            om.lobbying_firm
                and
            om.parent_entity_id is null
                and    
            (seat is not null and seat != '')
;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_seat_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_seat_org (cycle, rank_by_count)';
create index ranked_lobbying_orgs_by_seat_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_seat (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_seat_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_seat_org (cycle, rank_by_amount)';
create index ranked_lobbying_orgs_by_seat_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_seat (cycle, rank_by_amount);


-- CONTRIBUTIONS FROM LOBBYING ORGS BY INDIV/PAC
-- SELECT 21584
-- Time: 681.073 ms
-- CREATE INDEX
-- Time: 43.582 ms
-- CREATE INDEX
-- Time: 43.313 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_lobbying_orgs_by_indiv_pac';
drop table if exists ranked_lobbying_orgs_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table ranked_lobbying_orgs_by_indiv_pac';
create table ranked_lobbying_orgs_by_indiv_pac as
        select
            direct_or_indiv,
            om.cycle,
            organization_entity as lobbying_org_entity,
            me.name as lobbying_org_name,
            count,
            amount,
            rank() over(partition by direct_or_indiv, om.cycle order by count desc) as rank_by_count,
            rank() over(partition by direct_or_indiv, om.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_by_indiv_pac aots on me.id = aots.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle
        where
            om.lobbying_firm
            and
            om.parent_entity_id is null
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_indiv_pac_org (cycle, rank_by_count)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_count_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_indiv_pac_org (cycle, rank_by_amount)';
create index ranked_lobbying_orgs_by_indiv_pac_cycle_rank_by_amount_idx on ranked_lobbying_orgs_by_indiv_pac (cycle, rank_by_amount);




-- CONTRIBUTIONS FROM BIGGEST POL GROUPS BY PARTY
-- SELECT 6962
-- Time: 345.988 ms
-- CREATE INDEX
-- Time: 16.594 ms
-- CREATE INDEX
-- Time: 15.612 ms


select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_party';
drop table if exists ranked_pol_groups_by_party;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_party';
create table ranked_pol_groups_by_party as

        select
            recipient_party,
            cycle,
            organization_entity as pol_group_entity,
            organization_name as pol_group_name,
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
            om.is_pol_group
            and
            om.parent_entity_id is null
                and    
            (recipient_party is not null and recipient_party != '')
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id)
            ) three_party
        group by recipient_party, cycle, organization_entity, organization_name;

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_party_cycle_rank_idx ranked_pol_groups_by_party (cycle, rank_by_count)';
create index ranked_pol_groups_by_party_cycle_rank_by_count_idx on ranked_pol_groups_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_party_cycle_rank_idx ranked_pol_groups_by_party (cycle, rank_by_amount)';
create index ranked_pol_groups_by_party_cycle_rank_by_amount_idx on ranked_pol_groups_by_party (cycle, rank_by_amount);



-- CONTRIBUTIONS FROM BIGGEST POL GROUPS BY FEDERAL/STATE
-- SELECT 5635
-- Time: 329.071 ms
-- CREATE INDEX
-- Time: 13.655 ms
-- CREATE INDEX
-- Time: 16.845 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_state_fed';
drop table if exists ranked_pol_groups_by_state_fed;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_state_fed';
create table ranked_pol_groups_by_state_fed as
        select
            state_or_federal,
            aosf.cycle,
            aosf.organization_entity as pol_group_entity,
            me.name as pol_group_name,
            count,
            amount,
            rank() over(partition by state_or_federal, aosf.cycle order by count desc) as rank_by_count,
            rank() over(partition by state_or_federal, aosf.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_state_fed aosf on me.id = aosf.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = aosf.organization_entity and om.cycle = aosf.cycle
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
-- SELECT 14151
-- Time: 666.213 ms
-- CREATE INDEX
-- Time: 30.405 ms
-- CREATE INDEX
-- Time: 28.920 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_seat';
drop table if exists ranked_pol_groups_by_seat;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_seat';
create table ranked_pol_groups_by_seat as
        select
            aots.seat,
            aots.cycle,
            aots.organization_entity as pol_group_entity,
            me.name as pol_group_name,
            count,
            amount,
            rank() over(partition by aots.seat, aots.cycle order by count desc) as rank_by_count,
            rank() over(partition by aots.seat, aots.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_to_seat aots on me.id = aots.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle
        where
            om.is_pol_group
            and
            om.parent_entity_id is null
                and    
            (seat is not null and seat != '')
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_seat_cycle_rank_by_count_idx on ranked_pol_groups_by_seat_org (cycle, rank_by_count)';
create index ranked_pol_groups_by_seat_cycle_rank_by_count_idx on ranked_pol_groups_by_seat (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_seat_cycle_rank_by_amount_idx on ranked_pol_groups_by_seat_org (cycle, rank_by_amount)';
create index ranked_pol_groups_by_seat_cycle_rank_by_amount_idx on ranked_pol_groups_by_seat (cycle, rank_by_amount);

-- CONTRIBUTIONS FROM POL GROUPS BY INDIV/PAC
-- SELECT 21584
-- Time: 676.447 ms
-- CREATE INDEX
-- Time: 45.035 ms
-- CREATE INDEX
-- Time: 46.796 ms

select date_trunc('second', now()) || ' -- drop table if exists ranked_pol_groups_by_indiv_pac';
drop table if exists ranked_pol_groups_by_indiv_pac;

select date_trunc('second', now()) || ' -- create table ranked_pol_groups_by_indiv_pac';
create table ranked_pol_groups_by_indiv_pac as
        select
            direct_or_indiv,
            om.cycle,
            organization_entity as pol_group_entity,
            me.name as pol_group_name,
            count,
            amount,
            rank() over(partition by direct_or_indiv, om.cycle order by count desc) as rank_by_count,
            rank() over(partition by direct_or_indiv, om.cycle order by amount desc) as rank_by_amount
        from
                matchbox_entity me
            inner join
                aggregate_organization_by_indiv_pac aots on me.id = aots.organization_entity
            inner join
                matchbox_organizationmetadata om on om.entity_id = me.id and om.cycle = aots.cycle
        where
            om.lobbying_firm
            and
            om.parent_entity_id is null
            -- exists  (select 1 from biggest_organization_associations boa where apfo.organization_entity = boa.entity_id);
;

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_count_idx on ranked_pol_groups_by_indiv_pac_org (cycle, rank_by_count)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_count_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_count);

select date_trunc('second', now()) || ' -- create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_amount_idx on ranked_pol_groups_by_indiv_pac_org (cycle, rank_by_amount)';
create index ranked_pol_groups_by_indiv_pac_cycle_rank_by_amount_idx on ranked_pol_groups_by_indiv_pac (cycle, rank_by_amount);



