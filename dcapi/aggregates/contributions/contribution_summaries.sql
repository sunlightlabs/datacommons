select date_trunc('second', now()) || ' -- Starting contribution summary computation...';

\set agg_top_n 10

-- SUMMARY PARTY TOTALS AND TOP N ORGANIZATIONS

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

-- select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_party_cycle_rank_idx summary_parentmost_orgs_by_party (cycle, rank_by_count)';
-- create index summary_parentmost_orgs_by_party_cycle_rank_by_count_idx on summary_parentmost_orgs_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_party_cycle_rank_idx summary_parentmost_orgs_by_party (cycle, rank_by_amount)';
create index summary_parentmost_orgs_by_party_cycle_rank_by_amount_idx on summary_parentmost_orgs_by_party (cycle, rank_by_amount);

-- SUMMARY STATE/FEDERAL TOTALS AND TOP N ORGANIZATIONS

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

-- select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_state_fed_cycle_rank_by_count_idx on summary_parentmost_orgs_by_state_fed (cycle, rank_by_count)';
-- create index summary_parentmost_orgs_by_state_fed_cycle_rank_by_count_idx on summary_parentmost_orgs_by_state_fed (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_state_fed_cycle_rank_by_amount_idx on summary_parentmost_orgs_by_state_fed (cycle, rank_by_amount)';
create index summary_parentmost_orgs_by_state_fed_cycle_rank_by_amount_idx on summary_parentmost_orgs_by_state_fed (cycle, rank_by_amount);


-- SUMMARY SEAT TOTALS AND TOP N ORGANIZATIONS

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

-- select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_seat_cycle_rank_by_count_idx on summary_parentmost_orgs_by_seat_org (cycle, rank_by_count)';
-- create index summary_parentmost_orgs_by_seat_cycle_rank_by_count_idx on summary_parentmost_orgs_by_seat (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_seat_cycle_rank_by_amount_idx on summary_parentmost_orgs_by_seat_org (cycle, rank_by_amount)';
create index summary_parentmost_orgs_by_seat_cycle_rank_by_amount_idx on summary_parentmost_orgs_by_seat (cycle, rank_by_amount);




select date_trunc('second', now()) || ' -- create table summary_parentmost_orgs_by_indiv_pac';
create table summary_parentmost_orgs_by_indiv_pac as
select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_indiv_pac_cycle_rank_by_count_idx on summary_parentmost_orgs_by_indiv_pac_org (cycle, rank_by_count)';
create index summary_parentmost_orgs_by_indiv_pac_cycle_rank_by_count_idx on summary_parentmost_orgs_by_indiv_pac (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_parentmost_orgs_by_indiv_pac_cycle_rank_by_amount_idx on summary_parentmost_orgs_by_indiv_pac_org (cycle, rank_by_amount)';
create index summary_parentmost_orgs_by_indiv_pac_cycle_rank_by_amount_idx on summary_parentmost_orgs_by_indiv_pac (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_individuals_by_party';
create table summary_individuals_by_party as
select date_trunc('second', now()) || ' -- create index summary_individuals_by_party_cycle_rank_by_count_idx on summary_individuals_by_party (cycle, rank_by_count)';
create index summary_individuals_by_party_cycle_count_idx on summary_individuals_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_individuals_by_party_cycle_rank_by_amount_idx on summary_individuals_by_party (cycle, rank_by_amount)';
create index summary_individuals_by_party_cycle_amount_idx on summary_individuals_by_party (cycle, rank_by_amount);
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_state_fed';
 create table summary_individuals_by_state_fed as
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_state_fed_cycle_rank_by_count_idx on summary_individuals_by_state_fed (cycle, rank_by_count)';
 create index summary_individuals_by_state_fed_cycle_rank_by_count_idx on summary_individuals_by_state_fed (cycle, rank_by_count);
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_state_fed_cycle_rank_by_amount_idx on summary_individuals_by_state_fed (cycle, rank_by_amount)';
 create index summary_individuals_by_state_fed_cycle_rank_by_amount_idx on summary_individuals_by_state_fed (cycle, rank_by_amount);
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_seat';
 create table summary_individuals_by_seat as
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_seat_cycle_rank_by_count_idx on summary_individuals_by_seat (cycle, rank_by_count)';
 create index summary_individuals_by_seat_cycle_rank_by_count_idx on summary_individuals_by_seat (cycle, rank_by_count);
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_seat_cycle_rank_by_amount_idx on summary_individuals_by_seat (cycle, rank_by_amount)';
 create index summary_individuals_by_seat_cycle_rank_by_amount_idx on summary_individuals_by_seat (cycle, rank_by_amount);
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_recipient_type';
 create table summary_individuals_by_recipient_type as
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_recipient_type_cycle_rank_by_count_idx on summary_individuals_by_recipient_type (cycle, rank_by_count)';
 create index summary_individuals_by_recipient_type_cycle_rank_by_count_idx on summary_individuals_by_recipient_type (cycle, rank_by_count);
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_recipient_type_cycle_rank_by_amount_idx on summary_individuals_by_recipient_type (cycle, rank_by_amount)';
 create index summary_individuals_by_recipient_type_cycle_rank_by_amount_idx on summary_individuals_by_recipient_type (cycle, rank_by_amount);
 select date_trunc('second', now()) || ' -- create table summary_individuals_by_in_state_out_of_state';
 create table summary_individuals_by_in_state_out_of_state as
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_in_state_out_of_state_cycle_rank_by_count_idx on summary_individuals_by_in_state_out_of_state (cycle, rank_by_count)';
 create index summary_individuals_by_in_state_out_of_state_cycle_rank_by_count_idx on summary_individuals_by_in_state_out_of_state (cycle, rank_by_count);
 select date_trunc('second', now()) || ' -- create index summary_individuals_by_in_state_out_of_state_cycle_rank_by_amount_idx on summary_individuals_by_in_state_out_of_state (cycle, rank_by_amount)';
 create index summary_individuals_by_in_state_out_of_state_cycle_rank_by_amount_idx on summary_individuals_by_in_state_out_of_state (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_party';
create table summary_lobbyists_by_party as
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_party_cycle_rank_by_count_idx on summary_lobbyists_by_party (cycle, rank_by_count)';
create index summary_lobbyists_by_party_count_idx on summary_lobbyists_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_party_cycle_rank_by_amount_idx on summary_lobbyists_by_party (cycle, rank_by_amount)';
create index summary_lobbyists_by_party_amount_idx on summary_lobbyists_by_party (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_state_fed';
create table summary_lobbyists_by_state_fed as
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_state_fed_cycle_rank_by_count_idx on summary_lobbyists_by_state_fed (cycle, rank_by_count)';
create index summary_lobbyists_by_state_fed_cycle_rank_by_count_idx on summary_lobbyists_by_state_fed (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_state_fed_cycle_rank_by_amount_idx on summary_lobbyists_by_state_fed (cycle, rank_by_amount)';
create index summary_lobbyists_by_state_fed_cycle_rank_by_amount_idx on summary_lobbyists_by_state_fed (cycle, rank_by_amount);
 select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_seat';
 create table summary_lobbyists_by_seat as
 select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_seat_cycle_rank_by_count_idx on summary_lobbyists_by_seat (cycle, rank_by_count)';
 create index summary_lobbyists_by_seat_cycle_rank_by_count_idx on summary_lobbyists_by_seat (cycle, rank_by_count);
 select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_seat_cycle_rank_by_amount_idx on summary_lobbyists_by_seat (cycle, rank_by_amount)';
 create index summary_lobbyists_by_seat_cycle_rank_by_amount_idx on summary_lobbyists_by_seat (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_recipient_type';
create table summary_lobbyists_by_recipient_type as
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_recipient_type_cycle_rank_by_count_idx on summary_lobbyists_by_recipient_type (cycle, rank_by_count)';
create index summary_lobbyists_by_recipient_type_cycle_rank_by_count_idx on summary_lobbyists_by_recipient_type (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_recipient_type_cycle_rank_by_amount_idx on summary_lobbyists_by_recipient_type (cycle, rank_by_amount)';
create index summary_lobbyists_by_recipient_type_cycle_rank_by_amount_idx on summary_lobbyists_by_recipient_type (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbyists_by_in_state_out_of_state';
create table summary_lobbyists_by_in_state_out_of_state as
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_in_state_out_of_state_cycle_rank_by_count_idx on summary_lobbyists_by_in_state_out_of_state (cycle, rank_by_count)';
create index summary_lobbyists_by_in_state_out_of_state_cycle_rank_by_count_idx on summary_lobbyists_by_in_state_out_of_state (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbyists_by_in_state_out_of_state_cycle_rank_by_amount_idx on summary_lobbyists_by_in_state_out_of_state (cycle, rank_by_amount)';
create index summary_lobbyists_by_in_state_out_of_state_cycle_rank_by_amount_idx on summary_lobbyists_by_in_state_out_of_state (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_party';
create table summary_lobbying_orgs_by_party as
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_party_cycle_rank_idx summary_lobbying_orgs_by_party (cycle, rank_by_count)';
create index summary_lobbying_orgs_by_party_cycle_rank_by_count_idx on summary_lobbying_orgs_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_party_cycle_rank_idx summary_lobbying_orgs_by_party (cycle, rank_by_amount)';
create index summary_lobbying_orgs_by_party_cycle_rank_by_amount_idx on summary_lobbying_orgs_by_party (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_state_fed';
create table summary_lobbying_orgs_by_state_fed as
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_state_fed_cycle_rank_by_count_idx on summary_lobbying_orgs_by_state_fed (cycle, rank_by_count)';
create index summary_lobbying_orgs_by_state_fed_cycle_rank_by_count_idx on summary_lobbying_orgs_by_state_fed (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_state_fed_cycle_rank_by_amount_idx on summary_lobbying_orgs_by_state_fed (cycle, rank_by_amount)';
create index summary_lobbying_orgs_by_state_fed_cycle_rank_by_amount_idx on summary_lobbying_orgs_by_state_fed (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_seat';
create table summary_lobbying_orgs_by_seat as
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_seat_cycle_rank_by_count_idx on summary_lobbying_orgs_by_seat_org (cycle, rank_by_count)';
create index summary_lobbying_orgs_by_seat_cycle_rank_by_count_idx on summary_lobbying_orgs_by_seat (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_seat_cycle_rank_by_amount_idx on summary_lobbying_orgs_by_seat_org (cycle, rank_by_amount)';
create index summary_lobbying_orgs_by_seat_cycle_rank_by_amount_idx on summary_lobbying_orgs_by_seat (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_lobbying_orgs_by_indiv_pac';
create table summary_lobbying_orgs_by_indiv_pac as
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_indiv_pac_cycle_rank_by_count_idx on summary_lobbying_orgs_by_indiv_pac_org (cycle, rank_by_count)';
create index summary_lobbying_orgs_by_indiv_pac_cycle_rank_by_count_idx on summary_lobbying_orgs_by_indiv_pac (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_lobbying_orgs_by_indiv_pac_cycle_rank_by_amount_idx on summary_lobbying_orgs_by_indiv_pac_org (cycle, rank_by_amount)';
create index summary_lobbying_orgs_by_indiv_pac_cycle_rank_by_amount_idx on summary_lobbying_orgs_by_indiv_pac (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_party';
create table summary_pol_groups_by_party as
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_party_cycle_rank_idx summary_pol_groups_by_party (cycle, rank_by_count)';
create index summary_pol_groups_by_party_cycle_rank_by_count_idx on summary_pol_groups_by_party (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_party_cycle_rank_idx summary_pol_groups_by_party (cycle, rank_by_amount)';
create index summary_pol_groups_by_party_cycle_rank_by_amount_idx on summary_pol_groups_by_party (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_state_fed';
create table summary_pol_groups_by_state_fed as
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_state_fed_cycle_rank_by_count_idx on summary_pol_groups_by_state_fed (cycle, rank_by_count)';
create index summary_pol_groups_by_state_fed_cycle_rank_by_count_idx on summary_pol_groups_by_state_fed (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_state_fed_cycle_rank_by_amount_idx on summary_pol_groups_by_state_fed (cycle, rank_by_amount)';
create index summary_pol_groups_by_state_fed_cycle_rank_by_amount_idx on summary_pol_groups_by_state_fed (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_seat';
create table summary_pol_groups_by_seat as
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_seat_cycle_rank_by_count_idx on summary_pol_groups_by_seat_org (cycle, rank_by_count)';
create index summary_pol_groups_by_seat_cycle_rank_by_count_idx on summary_pol_groups_by_seat (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_seat_cycle_rank_by_amount_idx on summary_pol_groups_by_seat_org (cycle, rank_by_amount)';
create index summary_pol_groups_by_seat_cycle_rank_by_amount_idx on summary_pol_groups_by_seat (cycle, rank_by_amount);
select date_trunc('second', now()) || ' -- create table summary_pol_groups_by_indiv_pac';
create table summary_pol_groups_by_indiv_pac as
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_indiv_pac_cycle_rank_by_count_idx on summary_pol_groups_by_indiv_pac_org (cycle, rank_by_count)';
create index summary_pol_groups_by_indiv_pac_cycle_rank_by_count_idx on summary_pol_groups_by_indiv_pac (cycle, rank_by_count);
select date_trunc('second', now()) || ' -- create index summary_pol_groups_by_indiv_pac_cycle_rank_by_amount_idx on summary_pol_groups_by_indiv_pac_org (cycle, rank_by_amount)';
create index summary_pol_groups_by_indiv_pac_cycle_rank_by_amount_idx on summary_pol_groups_by_indiv_pac (cycle, rank_by_amount);
