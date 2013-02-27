create or replace function fec_candidates_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2014 ) then
        insert into fec_candidates_14 values (new.*)
    elsif (NEW.cycle = 2012 ) then
        insert into fec_candidates_12 values (new.*)
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!'
    else
        raise exception 'Cycle out of range! Fix the fec_candidates_insert_trigger() function!'
    end if;
    return null;
end;
$$
language plpgsql;

create trigger insert_fec_candidates_trigger
    before insert on fec_candidates
    for each row execute procedure fec_candidates_insert_trigger();


create or replace function fec_committees_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2014 ) then
        insert into fec_committees_14 values (new.*)
    elsif (NEW.cycle = 2012 ) then
        insert into fec_committees_12 values (new.*)
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!'
    else
        raise exception 'Cycle out of range! Fix the fec_committees_insert_trigger() function!'
    end if;
    return null;
end;
$$
language plpgsql;

create trigger insert_fec_committees_trigger
    before insert on fec_committees
    for each row execute procedure fec_committees_insert_trigger();


create or replace function fec_indiv_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2014 ) then
        insert into fec_indiv_14 values (new.*)
    elsif (NEW.cycle = 2012 ) then
        insert into fec_indiv_12 values (new.*)
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!'
    else
        raise exception 'Cycle out of range! Fix the fec_indiv_insert_trigger() function!'
    end if;
    return null;
end;
$$
language plpgsql;

create trigger insert_fec_indiv_trigger
    before insert on fec_indiv
    for each row execute procedure fec_indiv_insert_trigger();


create or replace function fec_pac2cand_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2014 ) then
        insert into fec_pac2cand_14 values (new.*)
    elsif (NEW.cycle = 2012 ) then
        insert into fec_pac2cand_12 values (new.*)
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!'
    else
        raise exception 'Cycle out of range! Fix the fec_pac2cand_insert_trigger() function!'
    end if;
    return null;
end;
$$
language plpgsql;

create trigger insert_fec_pac2cand_trigger
    before insert on fec_pac2cand
    for each row execute procedure fec_pac2cand_insert_trigger();


create or replace function fec_pac2pac_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2014 ) then
        insert into fec_pac2pac_14 values (new.*)
    elsif (NEW.cycle = 2012 ) then
        insert into fec_pac2pac_12 values (new.*)
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!'
    else
        raise exception 'Cycle out of range! Fix the fec_pac2pac_insert_trigger() function!'
    end if;
    return null;
end;
$$
language plpgsql;

create trigger insert_fec_pac2pac_trigger
    before insert on fec_pac2pac
    for each row execute procedure fec_pac2pac_insert_trigger();


create or replace function fec_candidate_summaries_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2014 ) then
        insert into fec_candidate_summaries_14 values (new.*)
    elsif (NEW.cycle = 2012 ) then
        insert into fec_candidate_summaries_12 values (new.*)
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!'
    else
        raise exception 'Cycle out of range! Fix the fec_candidate_summaries_insert_trigger() function!'
    end if;
    return null;
end;
$$
language plpgsql;

create trigger insert_fec_candidate_summaries_trigger
    before insert on fec_candidate_summaries
    for each row execute procedure fec_candidate_summaries_insert_trigger();


create or replace function fec_committee_summaries_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2014 ) then
        insert into fec_committee_summaries_14 values (new.*)
    elsif (NEW.cycle = 2012 ) then
        insert into fec_committee_summaries_12 values (new.*)
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!'
    else
        raise exception 'Cycle out of range! Fix the fec_committee_summaries_insert_trigger() function!'
    end if;
    return null;
end;
$$
language plpgsql;

create trigger insert_fec_committee_summaries_trigger
    before insert on fec_committee_summaries
    for each row execute procedure fec_committee_summaries_insert_trigger();
