select date_trunc('second', now()) || ' -- Starting contribution summary computation...';

\set agg_top_n 10

-- SUMMARY ENTITY TYPES
select date_trunc('second', now()) || ' -- drop table summary_entity_types';
drop table if exists summary_entity_types;

select date_trunc('second', now()) || ' -- create table summary_entity_types';
create table summary_entity_types as

        (select
            'industry' as entity_type,
            cycle,
            sum(count) as contributions_count,
            sum(amount) as contributions_amount,
            count(distinct industry_entity) as entity_count
        from
            ranked_industries_by_state_fed
        group by cycle) 

    union all

        (select
            'org' as entity_type,
            cycle,
            sum(count) as contributions_count,
            sum(amount) as contributions_amount,
            count(distinct organization_entity) as entity_count
        from
            ranked_parentmost_orgs_by_state_fed
        group by cycle) 

    union all

        (select
            'pol_group' as entity_type,
            cycle,
            sum(count) as contributions_count,
            sum(amount) as contributions_amount,
            count(distinct pol_group_entity) as entity_count
        from
            ranked_pol_groups_by_state_fed
        group by cycle) 

    union all
        
        (select
            'lobbying_org' as entity_type,
            cycle,
            sum(count) as contributions_count,
            sum(amount) as contributions_amount,
            count(distinct lobbying_org_entity) as entity_count
        from
            ranked_lobbying_orgs_by_state_fed
        group by cycle) 

    union all
        
        (select
            'individual' as entity_type,
            cycle,
            sum(count) as contributions_count,
            sum(amount) as contributions_amount,
            count(distinct individual_entity) as entity_count
        from
            ranked_individuals_by_state_fed
        group by cycle) 

    union all

        (select
            'lobbyist' as entity_type,
            cycle,
            sum(count) as contributions_count,
            sum(amount) as contributions_amount,
            count(distinct lobbyist_entity) as entity_count
        from
            ranked_lobbyists_by_state_fed
        group by cycle)

    union all

        (select
            'pol' as entity_type,
            cycle,
            sum(count) as contributions_count,
            sum(amount) as contributions_amount,
            count(distinct politician_entity) as entity_count
        from
            ranked_politicians_by_org_pac_indiv
        group by cycle)
    ;

    
-- SUMMARY recipient_party TOTALS AND TOP N ORGANIZATIONS
select date_trunc('second', now()) || ' -- drop table summary_parentmost_orgs_by_party';
drop table if exists summary_parentmost_orgs_by_party;

select date_trunc('second', now()) || ' -- create table summary_parentmost_orgs_by_party';
create table summary_parentmost_orgs_by_party as
    with party_totals as 
        ( 
            select
                recipient_party,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_parentmost_orgs_by_party
            group by
                recipient_party,
                cycle
            )

    select
        rop.recipient_party, 
        rop.cycle,
        pt.total_count,
        pt.total_amount,
        rop.organization_entity, 
        rop.organization_name, 
        rop.count,
        rop.amount,
        rop.rank_by_count,
        rop.rank_by_amount
    from
        ranked_parentmost_orgs_by_party rop
            inner join
        party_totals pt using (recipient_party, cycle)
    where
        rop.rank_by_amount <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_party_cycle_idx summary_parentmost_orgs_by_party (cycle)';
create index summary_parentmost_orgs_by_party_cycle_idx on summary_parentmost_orgs_by_party (cycle);

-- SUMMARY STATE/FEDERAL TOTALS AND TOP N ORGANIZATIONS
select date_trunc('second', now()) || ' -- drop table summary_parentmost_orgs_by_state_fed';
drop table if exists summary_parentmost_orgs_by_state_fed;

select date_trunc('second', now()) || ' -- create table summary_parentmost_orgs_by_state_fed';
create table summary_parentmost_orgs_by_state_fed as
    with state_fed_totals as 
        ( 
            select
                state_or_federal,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_parentmost_orgs_by_state_fed
            group by
                state_or_federal,
                cycle
            )

    select
        rosf.state_or_federal, 
        rosf.cycle,
        pt.total_count,
        pt.total_amount,
        rosf.organization_entity, 
        rosf.organization_name, 
        rosf.count,
        rosf.amount,
        rosf.rank_by_count,
        rosf.rank_by_amount
    from
        ranked_parentmost_orgs_by_state_fed rosf
            inner join
        state_fed_totals pt using (state_or_federal, cycle)
    where
        rosf.rank_by_amount <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_state_fed_cycle_idx summary_parentmost_orgs_by_state_fed (cycle)';
create index summary_parentmost_orgs_by_state_fed_cycle_idx on summary_parentmost_orgs_by_state_fed (cycle);


-- SUMMARY SEAT TOTALS AND TOP N ORGANIZATIONS
select date_trunc('second', now()) || ' -- drop table summary_parentmost_orgs_by_seat';
drop table if exists summary_parentmost_orgs_by_seat;

select date_trunc('second', now()) || ' -- create table summary_parentmost_orgs_by_seat';
create table summary_parentmost_orgs_by_seat as
    with seat_totals as 
        ( 
            select
                seat,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_parentmost_orgs_by_seat
            group by
                seat,
                cycle
            )

    select
        ros.seat, 
        ros.cycle,
        pt.total_count,
        pt.total_amount,
        ros.organization_entity, 
        ros.organization_name, 
        ros.count,
        ros.amount,
        ros.rank_by_count,
        ros.rank_by_amount
    from
        ranked_parentmost_orgs_by_seat ros
            inner join
        seat_totals pt using (seat, cycle)
    where
        ros.rank_by_amount <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_seat_cycle_idx summary_parentmost_orgs_by_seat (cycle)';
create index summary_parentmost_orgs_by_seat_cycle_idx on summary_parentmost_orgs_by_seat (cycle);

-- SUMMARY INDIV/PAC TOTALS AND TOP N ORGANIZATIONS
select date_trunc('second', now()) || ' -- drop table summary_parentmost_orgs_by_indiv_pac';
drop table if exists summary_parentmost_orgs_by_indiv_pac;


select date_trunc('second', now()) || ' -- create table summary_parentmost_orgs_by_indiv_pac';
create table summary_parentmost_orgs_by_indiv_pac as
    with indiv_pac_totals as 
        ( 
            select
                direct_or_indiv,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_parentmost_orgs_by_indiv_pac
            group by
                direct_or_indiv,
                cycle
            )

    select
        roip.direct_or_indiv, 
        roip.cycle,
        pt.total_count,
        pt.total_amount,
        roip.organization_entity, 
        roip.organization_name, 
        roip.count,
        roip.amount,
        roip.rank_by_count,
        roip.rank_by_amount
    from
        ranked_parentmost_orgs_by_indiv_pac roip
            inner join
        indiv_pac_totals pt using (direct_or_indiv, cycle)
    where
        roip.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_indiv_pac_cycle_idx summary_parentmost_orgs_by_indiv_pac (cycle)';
create index summary_parentmost_orgs_by_indiv_pac_cycle_idx on summary_parentmost_orgs_by_indiv_pac (cycle);

-- SUMMARY RECIPIENT TYPE TOTALS AND TOP N PARENTMOST ORGS
select date_trunc('second', now()) || ' -- drop table summary_parentmost_orgs_by_recipient_type';
drop table if exists summary_parentmost_orgs_by_recipient_type;
 select date_trunc('second', now()) || ' -- create table summary_parentmost_orgs_by_recipient_type';
 create table summary_parentmost_orgs_by_recipient_type as
    with recipient_type_totals as 
        ( 
            select
                recipient_type,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_parentmost_orgs_by_recipient_type
            group by
                recipient_type,
                cycle
            )

    select
        ris.recipient_type, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.organization_entity, 
        ris.organization_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_parentmost_orgs_by_recipient_type ris
            inner join
        recipient_type_totals pt using (recipient_type, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_recipient_type_cycle_idx summary_parentmost_orgs_by_recipient_type (cycle)';
create index summary_parentmost_orgs_by_recipient_type_cycle_idx on summary_parentmost_orgs_by_recipient_type (cycle);


-- SUMMARY PARTY TOTALS AND TOP N INDIVIDUALS
select date_trunc('second', now()) || ' -- drop table summary_individuals_by_party';
drop table if exists summary_individuals_by_party;

select date_trunc('second', now()) || ' -- create table summary_individuals_by_party';
create table summary_individuals_by_party as
    with party_totals as 
        ( 
            select
                recipient_party,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_individuals_by_party
            group by
                recipient_party,
                cycle
            )

    select
        rop.recipient_party, 
        rop.cycle,
        pt.total_count,
        pt.total_amount,
        rop.individual_entity, 
        rop.individual_name, 
        rop.count,
        rop.amount,
        rop.rank_by_count,
        rop.rank_by_amount
    from
        ranked_individuals_by_party rop
            inner join
        party_totals pt using (recipient_party, cycle)
    where
        rop.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_individuals_by_party_cycle_idx summary_individuals_by_party (cycle)';
create index summary_individuals_by_party_cycle_idx on summary_individuals_by_party (cycle);


-- SUMMARY STATE/FEDERAL TOTALS AND TOP N INDIVIDUALS
select date_trunc('second', now()) || ' -- drop table summary_individuals_by_state_fed';
drop table if exists summary_individuals_by_state_fed;
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_state_fed';
 create table summary_individuals_by_state_fed as
    with state_fed_totals as 
        ( 
            select
                state_or_federal,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_individuals_by_state_fed
            group by
                state_or_federal,
                cycle
            )

    select
        rosf.state_or_federal, 
        rosf.cycle,
        pt.total_count,
        pt.total_amount,
        rosf.individual_entity, 
        rosf.individual_name, 
        rosf.count,
        rosf.amount,
        rosf.rank_by_count,
        rosf.rank_by_amount
    from
        ranked_individuals_by_state_fed rosf
            inner join
        state_fed_totals pt using (state_or_federal, cycle)
    where
        rosf.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_individuals_by_state_fed_cycle_idx summary_individuals_by_state_fed (cycle)';
create index summary_individuals_by_state_fed_cycle_idx on summary_individuals_by_state_fed (cycle);

-- SUMMARY SEAT TOTALS AND TOP N INDIVIDUALS
select date_trunc('second', now()) || ' -- drop table summary_individuals_by_seat';
drop table if exists summary_individuals_by_seat;
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_seat';
 create table summary_individuals_by_seat as
    with seat_totals as 
        ( 
            select
                seat,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_individuals_by_seat
            group by
                seat,
                cycle
            )

    select
        ris.seat, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.individual_entity, 
        ris.individual_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_individuals_by_seat ris
            inner join
        seat_totals pt using (seat, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_individuals_by_seat_cycle_idx summary_individuals_by_seat (cycle)';
create index summary_individuals_by_seat_cycle_idx on summary_individuals_by_seat (cycle);

-- SUMMARY RECIPIENT TYPE TOTALS AND TOP N INDIVIDUALS
select date_trunc('second', now()) || ' -- drop table summary_individuals_by_recipient_type';
drop table if exists summary_individuals_by_recipient_type;
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_recipient_type';
 create table summary_individuals_by_recipient_type as
    with recipient_type_totals as 
        ( 
            select
                recipient_type,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_individuals_by_recipient_type
            group by
                recipient_type,
                cycle
            )

    select
        ris.recipient_type, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.individual_entity, 
        ris.individual_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_individuals_by_recipient_type ris
            inner join
        recipient_type_totals pt using (recipient_type, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_individuals_by_recipient_type_cycle_idx summary_individuals_by_recipient_type (cycle)';
create index summary_individuals_by_recipient_type_cycle_idx on summary_individuals_by_recipient_type (cycle);

select date_trunc('second', now()) || ' -- drop table summary_individuals_by_in_state_out_of_state';
drop table if exists summary_individuals_by_in_state_out_of_state;
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_in_state_out_of_state';
 create table summary_individuals_by_in_state_out_of_state as
    with in_state_out_of_state_totals as 
        ( 
            select
                in_state_out_of_state,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_individuals_by_in_state_out_of_state
            group by
                in_state_out_of_state,
                cycle
            )

    select
        ris.in_state_out_of_state, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.individual_entity, 
        ris.individual_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_individuals_by_in_state_out_of_state ris
            inner join
        in_state_out_of_state_totals pt using (in_state_out_of_state, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_individuals_by_in_out_of_state_cycle_idx summary_individuals_by_in_state_out_of_state (cycle)';
create index summary_individuals_by_in_out_of_state_cycle_idx on summary_individuals_by_in_state_out_of_state (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbyists_by_party';
drop table if exists summary_lobbyists_by_party;
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_party';
create table summary_lobbyists_by_party as
    with party_totals as 
        ( 
            select
                recipient_party,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbyists_by_party
            group by
                recipient_party,
                cycle
            )

    select
        ris.recipient_party, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbyist_entity, 
        ris.lobbyist_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbyists_by_party ris
            inner join
        party_totals pt using (recipient_party, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_party_cycle_idx summary_lobbyists_by_party (cycle)';
create index summary_lobbyists_by_party_cycle_idx on summary_lobbyists_by_party (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbyists_by_state_fed';
drop table if exists summary_lobbyists_by_state_fed;
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_state_fed';
create table summary_lobbyists_by_state_fed as
    with state_fed_totals as 
        ( 
            select
                state_or_federal,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbyists_by_state_fed
            group by
                state_or_federal,
                cycle
            )

    select
        ris.state_or_federal, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbyist_entity, 
        ris.lobbyist_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbyists_by_state_fed ris
            inner join
        state_fed_totals pt using (state_or_federal, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_state_fed_cycle_idx summary_lobbyists_by_state_fed (cycle)';
create index summary_lobbyists_by_state_fed_cycle_idx on summary_lobbyists_by_state_fed (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbyists_by_seat';
drop table if exists summary_lobbyists_by_seat;
 select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_seat';
 create table summary_lobbyists_by_seat as
    with seat_totals as 
        ( 
            select
                seat,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbyists_by_seat
            group by
                seat,
                cycle
            )

    select
        ris.seat, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbyist_entity, 
        ris.lobbyist_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbyists_by_seat ris
            inner join
        seat_totals pt using (seat, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_seat_cycle_idx summary_lobbyists_by_seat (cycle)';
create index summary_lobbyists_by_seat_cycle_idx on summary_lobbyists_by_seat (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbyists_by_recipient_type';
drop table if exists summary_lobbyists_by_recipient_type;
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_recipient_type';
create table summary_lobbyists_by_recipient_type as
    with recipient_type_totals as 
        ( 
            select
                recipient_type,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbyists_by_recipient_type
            group by
                recipient_type,
                cycle
            )

    select
        ris.recipient_type, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbyist_entity, 
        ris.lobbyist_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbyists_by_recipient_type ris
            inner join
        recipient_type_totals pt using (recipient_type, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_recipient_type_cycle_idx summary_lobbyists_by_recipient_type (cycle)';
create index summary_lobbyists_by_recipient_type_cycle_idx on summary_lobbyists_by_recipient_type (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbyists_by_in_state_out_of_state';
drop table if exists summary_lobbyists_by_in_state_out_of_state;
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_in_state_out_of_state';
create table summary_lobbyists_by_in_state_out_of_state as
    with in_state_out_of_state_totals as 
        ( 
            select
                in_state_out_of_state,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbyists_by_in_state_out_of_state
            group by
                in_state_out_of_state,
                cycle
            )

    select
        ris.in_state_out_of_state, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbyist_entity, 
        ris.lobbyist_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbyists_by_in_state_out_of_state ris
            inner join
        in_state_out_of_state_totals pt using (in_state_out_of_state, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_in_state_out_of_state_cycle_idx summary_lobbyists_by_in_state_out_of_state (cycle)';
create index summary_lobbyists_by_in_state_out_of_state_cycle_idx on summary_lobbyists_by_in_state_out_of_state (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbying_orgs_by_party';
drop table if exists summary_lobbying_orgs_by_party;
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_party';
create table summary_lobbying_orgs_by_party as
    with party_totals as 
        ( 
            select
                recipient_party,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbying_orgs_by_party
            group by
                recipient_party,
                cycle
            )

    select
        ris.recipient_party, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbying_org_entity, 
        ris.lobbying_org_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbying_orgs_by_party ris
            inner join
        party_totals pt using (recipient_party, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_party_cycle_idx summary_lobbying_orgs_by_party (cycle)';
create index summary_lobbying_orgs_by_party_cycle_idx on summary_lobbying_orgs_by_party (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbying_orgs_by_state_fed';
drop table if exists summary_lobbying_orgs_by_state_fed;
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_state_fed';
create table summary_lobbying_orgs_by_state_fed as
    with state_fed_totals as 
        ( 
            select
                state_or_federal,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbying_orgs_by_state_fed
            group by
                state_or_federal,
                cycle
            )

    select
        ris.state_or_federal, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbying_org_entity, 
        ris.lobbying_org_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbying_orgs_by_state_fed ris
            inner join
        state_fed_totals pt using (state_or_federal, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_state_fed_cycle_idx summary_lobbying_orgs_by_state_fed (cycle)';
create index summary_lobbying_orgs_by_state_fed_cycle_idx on summary_lobbying_orgs_by_state_fed (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbying_orgs_by_seat';
drop table if exists summary_lobbying_orgs_by_seat;
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_seat';
create table summary_lobbying_orgs_by_seat as
    with seat_totals as 
        ( 
            select
                seat,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbying_orgs_by_seat
            group by
                seat,
                cycle
            )

    select
        ris.seat, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbying_org_entity, 
        ris.lobbying_org_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbying_orgs_by_seat ris
            inner join
        seat_totals pt using (seat, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_seat_cycle_idx summary_lobbying_orgs_by_seat (cycle)';
create index summary_lobbying_orgs_by_seat_cycle_idx on summary_lobbying_orgs_by_seat (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbying_orgs_by_indiv_pac';
drop table if exists summary_lobbying_orgs_by_indiv_pac;
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_indiv_pac';
create table summary_lobbying_orgs_by_indiv_pac as
    with indiv_pac_totals as 
        ( 
            select
                direct_or_indiv,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbying_orgs_by_indiv_pac
            group by
                direct_or_indiv,
                cycle
            )

    select
        ris.direct_or_indiv, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbying_org_entity, 
        ris.lobbying_org_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbying_orgs_by_indiv_pac ris
            inner join
        indiv_pac_totals pt using (direct_or_indiv, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_indiv_pac_cycle_idx summary_lobbying_orgs_by_indiv_pac (cycle)';
create index summary_lobbying_orgs_by_indiv_pac_cycle_idx on summary_lobbying_orgs_by_indiv_pac (cycle);

select date_trunc('second', now()) || ' -- drop table summary_lobbying_orgs_by_recipient_type';
drop table if exists summary_lobbying_orgs_by_recipient_type;
 select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_recipient_type';
 create table summary_lobbying_orgs_by_recipient_type as
    with recipient_type_totals as 
        ( 
            select
                recipient_type,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_lobbying_orgs_by_recipient_type
            group by
                recipient_type,
                cycle
            )

    select
        ris.recipient_type, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.lobbying_org_entity, 
        ris.lobbying_org_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_lobbying_orgs_by_recipient_type ris
            inner join
        recipient_type_totals pt using (recipient_type, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_recipient_type_cycle_idx summary_lobbying_orgs_by_recipient_type (cycle)';
create index summary_lobbying_orgs_by_recipient_type_cycle_idx on summary_lobbying_orgs_by_recipient_type (cycle);


select date_trunc('second', now()) || ' -- drop table summary_pol_groups_by_party';
drop table if exists summary_pol_groups_by_party;
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_party';
create table summary_pol_groups_by_party as
    with party_totals as 
        ( 
            select
                recipient_party,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_pol_groups_by_party
            group by
                recipient_party,
                cycle
            )

    select
        ris.recipient_party, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.pol_group_entity, 
        ris.pol_group_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_pol_groups_by_party ris
            inner join
        party_totals pt using (recipient_party, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_party_cycle_idx summary_pol_groups_by_party (cycle)';
create index summary_pol_groups_by_party_cycle_idx on summary_pol_groups_by_party (cycle);

select date_trunc('second', now()) || ' -- drop table summary_pol_groups_by_state_fed';
drop table if exists summary_pol_groups_by_state_fed;
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_state_fed';
create table summary_pol_groups_by_state_fed as
    with state_fed_totals as 
        ( 
            select
                state_or_federal,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_pol_groups_by_state_fed
            group by
                state_or_federal,
                cycle
            )

    select
        ris.state_or_federal, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.pol_group_entity, 
        ris.pol_group_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_pol_groups_by_state_fed ris
            inner join
        state_fed_totals pt using (state_or_federal, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_state_fed_cycle_idx summary_pol_groups_by_state_fed (cycle)';
create index summary_pol_groups_by_state_fed_cycle_idx on summary_pol_groups_by_state_fed (cycle);

select date_trunc('second', now()) || ' -- drop table summary_pol_groups_by_seat';
drop table if exists summary_pol_groups_by_seat;
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_seat';
create table summary_pol_groups_by_seat as
    with seat_totals as 
        ( 
            select
                seat,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_pol_groups_by_seat
            group by
                seat,
                cycle
            )

    select
        ris.seat, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.pol_group_entity, 
        ris.pol_group_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_pol_groups_by_seat ris
            inner join
        seat_totals pt using (seat, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_seat_cycle_idx summary_pol_groups_by_seat (cycle)';
create index summary_pol_groups_by_seat_cycle_idx on summary_pol_groups_by_seat (cycle);

select date_trunc('second', now()) || ' -- drop table summary_pol_groups_by_indiv_pac';
drop table if exists summary_pol_groups_by_indiv_pac;
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_indiv_pac';
create table summary_pol_groups_by_indiv_pac as
    with indiv_pac_totals as 
        ( 
            select
                direct_or_indiv,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_pol_groups_by_indiv_pac
            group by
                direct_or_indiv,
                cycle
            )

    select
        ris.direct_or_indiv, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.pol_group_entity, 
        ris.pol_group_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_pol_groups_by_indiv_pac ris
            inner join
        indiv_pac_totals pt using (direct_or_indiv, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_indiv_pac_cycle_idx summary_pol_groups_by_indiv_pac (cycle)';
create index summary_pol_groups_by_indiv_pac_cycle_idx on summary_pol_groups_by_indiv_pac (cycle);

select date_trunc('second', now()) || ' -- drop table summary_pol_groups_by_recipient_type';
drop table if exists summary_pol_groups_by_recipient_type;
 select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_recipient_type';
 create table summary_pol_groups_by_recipient_type as
    with recipient_type_totals as 
        ( 
            select
                recipient_type,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_pol_groups_by_recipient_type
            group by
                recipient_type,
                cycle
            )

    select
        ris.recipient_type, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.pol_group_entity, 
        ris.pol_group_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_pol_groups_by_recipient_type ris
            inner join
        recipient_type_totals pt using (recipient_type, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_recipient_type_cycle_idx summary_pol_groups_by_recipient_type (cycle)';
create index summary_pol_groups_by_recipient_type_cycle_idx on summary_pol_groups_by_recipient_type (cycle);

-- SUMMARY PARTY TOTALS AND TOP N INDUSTRIES
select date_trunc('second', now()) || ' -- drop table summary_industries_by_party';
drop table if exists summary_industries_by_party;

select date_trunc('second', now()) || ' -- create table summary_industries_by_party';
create table summary_industries_by_party as
    with party_totals as 
        ( 
            select
                recipient_party,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_industries_by_party
            group by
                recipient_party,
                cycle
            )

    select
        rop.recipient_party, 
        rop.cycle,
        pt.total_count,
        pt.total_amount,
        rop.industry_entity, 
        rop.industry_name, 
        rop.count,
        rop.amount,
        rop.rank_by_count,
        rop.rank_by_amount
    from
        ranked_industries_by_party rop
            inner join
        party_totals pt using (recipient_party, cycle)
    where
        rop.rank_by_amount <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index summary_industries_by_party_cycle_idx summary_industries_by_party (cycle)';
create index summary_industries_by_party_cycle_idx on summary_industries_by_party (cycle);

-- SUMMARY STATE/FEDERAL TOTALS AND TOP N INDUSTRIES
select date_trunc('second', now()) || ' -- drop table summary_industries_by_state_fed';
drop table if exists summary_industries_by_state_fed;

select date_trunc('second', now()) || ' -- create table summary_industries_by_state_fed';
create table summary_industries_by_state_fed as
    with state_fed_totals as 
        ( 
            select
                state_or_federal,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_industries_by_state_fed
            group by
                state_or_federal,
                cycle
            )

    select
        rosf.state_or_federal, 
        rosf.cycle,
        pt.total_count,
        pt.total_amount,
        rosf.industry_entity, 
        rosf.industry_name, 
        rosf.count,
        rosf.amount,
        rosf.rank_by_count,
        rosf.rank_by_amount
    from
        ranked_industries_by_state_fed rosf
            inner join
        state_fed_totals pt using (state_or_federal, cycle)
    where
        rosf.rank_by_amount <= :agg_top_n
;

select date_trunc('second', now()) || ' -- create index summary_industries_by_state_fed_cycle_idx summary_industries_by_state_fed (cycle)';
create index summary_industries_by_state_fed_cycle_idx on summary_industries_by_state_fed (cycle);


-- -- SUMMARY SEAT TOTALS AND TOP N INDUSTRIES
-- select date_trunc('second', now()) || ' -- drop table summary_industries_by_seat';
-- drop table if exists summary_industries_by_seat;
-- 
-- select date_trunc('second', now()) || ' -- create table summary_industries_by_seat';
-- create table summary_industries_by_seat as
--     with seat_totals as 
--         ( 
--             select
--                 seat,
--                 cycle,
--                 sum(count) as total_count,
--                 sum(amount) as total_amount
--             from
--                 ranked_industries_by_seat
--             group by
--                 seat,
--                 cycle
--             )
-- 
--     select
--         ros.seat, 
--         ros.cycle,
--         pt.total_count,
--         pt.total_amount,
--         ros.industry_entity, 
--         ros.industry_name, 
--         ros.count,
--         ros.amount,
--         ros.rank_by_count,
--         ros.rank_by_amount
--     from
--         ranked_industries_by_seat ros
--             inner join
--         seat_totals pt using (seat, cycle)
--     where
--         ros.rank_by_amount <= :agg_top_n
-- ;
-- 
-- select date_trunc('second', now()) || ' -- create index summary_industries_by_seat_cycle_idx summary_industries_by_seat (cycle)';
-- create index summary_industries_by_seat_cycle_idx on summary_industries_by_seat (cycle);

-- SUMMARY INDIV/PAC TOTALS AND TOP N INDUSTRIES
select date_trunc('second', now()) || ' -- drop table summary_industries_by_indiv_pac';
drop table if exists summary_industries_by_indiv_pac;


select date_trunc('second', now()) || ' -- create table summary_industries_by_indiv_pac';
create table summary_industries_by_indiv_pac as
    with indiv_pac_totals as 
        ( 
            select
                direct_or_indiv,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_industries_by_indiv_pac
            group by
                direct_or_indiv,
                cycle
            )

    select
        roip.direct_or_indiv, 
        roip.cycle,
        pt.total_count,
        pt.total_amount,
        roip.industry_entity, 
        roip.industry_name, 
        roip.count,
        roip.amount,
        roip.rank_by_count,
        roip.rank_by_amount
    from
        ranked_industries_by_indiv_pac roip
            inner join
        indiv_pac_totals pt using (direct_or_indiv, cycle)
    where
        roip.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_industries_by_indiv_pac_cycle_idx summary_industries_by_indiv_pac (cycle)';
create index summary_industries_by_indiv_pac_cycle_idx on summary_industries_by_indiv_pac (cycle);

-- SUMMARY RECIPIENT TYPE TOTALS AND TOP N INDUSTRIES
select date_trunc('second', now()) || ' -- drop table summary_industries_by_recipient_type';
drop table if exists summary_industries_by_recipient_type;
 select date_trunc('second', now()) || ' -- create table summary_industries_by_recipient_type';
 create table summary_industries_by_recipient_type as
    with recipient_type_totals as 
        ( 
            select
                recipient_type,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_industries_by_recipient_type
            group by
                recipient_type,
                cycle
            )

    select
        ris.recipient_type, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.industry_entity, 
        ris.industry_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_industries_by_recipient_type ris
            inner join
        recipient_type_totals pt using (recipient_type, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_industries_by_recipient_type_cycle_idx summary_industries_by_recipient_type (cycle)';
create index summary_industries_by_recipient_type_cycle_idx on summary_industries_by_recipient_type (cycle);

-- SUMMARY RECIPIENT TYPE TOTALS AND TOP N INDUSTRIES
select date_trunc('second', now()) || ' -- drop table summary_industries_by_recipient_type';
drop table if exists summary_industries_by_recipient_type;
 select date_trunc('second', now()) || ' -- create table summary_industries_by_recipient_type';
 create table summary_industries_by_recipient_type as
    with recipient_type_totals as 
        ( 
            select
                recipient_type,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_industries_by_recipient_type
            group by
                recipient_type,
                cycle
            )

    select
        ris.recipient_type, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.industry_entity, 
        ris.industry_name, 
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_industries_by_recipient_type ris
            inner join
        recipient_type_totals pt using (recipient_type, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_industries_by_recipient_type_cycle_idx summary_industries_by_recipient_type (cycle)';
create index summary_industries_by_recipient_type_cycle_idx on summary_industries_by_recipient_type (cycle);

-- SUMMARY ORG/PAC/INDIV TOTALS AND TOP N POLITICIANS
select date_trunc('second', now()) || ' -- drop table summary_politicians_by_org_pac_indiv';
drop table if exists summary_politicians_by_org_pac_indiv;
 select date_trunc('second', now()) || ' -- create table summary_politicians_by_org_pac_indiv';
 create table summary_politicians_by_org_pac_indiv as
    with org_pac_indiv_totals as 
        ( 
            select
                org_pac_indiv,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_politicians_by_org_pac_indiv
            group by
                org_pac_indiv,
                cycle
            )

    select
        ris.org_pac_indiv, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.politician_entity,
        ris.politician_name,
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_politicians_by_org_pac_indiv ris
            inner join
        org_pac_indiv_totals pt using (org_pac_indiv, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_politicians_by_org_pac_indiv_cycle_idx summary_politicians_by_org_pac_indiv (cycle)';
create index summary_politicians_by_org_pac_indiv_cycle_idx on summary_politicians_by_org_pac_indiv (cycle);

-- SUMMARY IN STATE/OUT OF STATE TOTALS AND TOP N POLITICIANS
select date_trunc('second', now()) || ' -- drop table summary_politicians_from_individuals_by_in_state_out_of_state';
drop table if exists summary_politicians_from_individuals_by_in_state_out_of_state;
 select date_trunc('second', now()) || ' -- create table summary_politicians_from_individuals_by_in_state_out_of_state';
 create table summary_politicians_from_individuals_by_in_state_out_of_state as
    with in_state_out_of_state_totals as 
        ( 
            select
                in_state_out_of_state,
                cycle,
                sum(count) as total_count,
                sum(amount) as total_amount
            from
                ranked_politicians_from_individuals_by_in_state_out_of_state
            group by
                in_state_out_of_state,
                cycle
            )

    select
        ris.in_state_out_of_state, 
        ris.cycle,
        pt.total_count,
        pt.total_amount,
        ris.politician_entity,
        ris.politician_name,
        ris.count,
        ris.amount,
        ris.rank_by_count,
        ris.rank_by_amount
    from
        ranked_politicians_from_individuals_by_in_state_out_of_state ris
            inner join
        in_state_out_of_state_totals pt using (in_state_out_of_state, cycle)
    where
        ris.rank_by_amount <= :agg_top_n
;
select date_trunc('second', now()) || ' -- create index summary_politicians_from_individuals_by_in_state_out_of_state_cycle_idx summary_politicians_from_individuals_by_in_state_out_of_state (cycle)';
create index summary_politicians_from_individuals_by_in_state_out_of_state_cycle_idx on summary_politicians_from_individuals_by_in_state_out_of_state (cycle);

-- -- SUMMARY INDUSTRY TOTALS AND TOP N POLITICIANS
-- select date_trunc('second', now()) || ' -- drop table summary_politicians_from_industries';
-- drop table if exists summary_politicians_from_industries;
--  select date_trunc('second', now()) || ' -- create table summary_politicians_from_industries';
--  create table summary_politicians_from_industries as
--     with industry_entity_totals as 
--         ( 
--             select
--                 industry_entity,
--                 cycle,
--                 sum(count) as total_count,
--                 sum(amount) as total_amount
--             from
--                 ranked_politicians_from_industries
--             group by
--                 industry_entity,
--                 cycle
--             )
-- 
--     select
--         ris.industry_entity,
--         ris.industry_name, 
--         ris.cycle,
--         pt.total_count,
--         pt.total_amount,
--         ris.politician_entity,
--         ris.politician_name,
--         ris.count,
--         ris.amount,
--         ris.rank_by_count,
--         ris.rank_by_amount
--     from
--         ranked_politicians_from_industries ris
--             inner join
--         industry_entity_totals pt using (industry_entity, cycle)
--     where
--         ris.rank_by_amount <= :agg_top_n
-- ;
-- select date_trunc('second', now()) || ' -- create index summary_politicians_from_industries_cycle_idx summary_politicians_from_industries (cycle)';
-- create index summary_politicians_from_industries_cycle_idx on summary_politicians_from_industries (cycle);
-- 
commit;
