create or replace function fec_candidates_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2020 ) then
        insert into fec_candidates_20 values (new.*);
    elsif ( NEW.cycle = 2018 ) then
        insert into fec_candidates_18 values (new.*);
    elsif ( NEW.cycle = 2016 ) then
        insert into fec_candidates_16 values (new.*);
    elsif ( NEW.cycle = 2014 ) then
        insert into fec_candidates_14 values (new.*);
    elsif (NEW.cycle = 2012 ) then
        insert into fec_candidates_12 values (new.*);
    elsif (NEW.cycle = 2010 ) then
        insert into fec_candidates_10 values (new.*);
    elsif (NEW.cycle = 2008 ) then
        insert into fec_candidates_08 values (new.*);
    elsif (NEW.cycle = 2006 ) then
        insert into fec_candidates_06 values (new.*);
    elsif (NEW.cycle = 2004 ) then
        insert into fec_candidates_04 values (new.*);
    elsif (NEW.cycle = 2002 ) then
        insert into fec_candidates_02 values (new.*);
    elsif (NEW.cycle = 2000 ) then
        insert into fec_candidates_00 values (new.*);
    elsif (NEW.cycle = 1998 ) then
        insert into fec_candidates_98 values (new.*);
    elsif (NEW.cycle = 1996 ) then
        insert into fec_candidates_96 values (new.*);
    elsif (NEW.cycle = 1994 ) then
        insert into fec_candidates_94 values (new.*);
    elsif (NEW.cycle = 1992 ) then
        insert into fec_candidates_92 values (new.*);
    elsif (NEW.cycle = 1990 ) then
        insert into fec_candidates_90 values (new.*);
    elsif (NEW.cycle = 1988 ) then
        insert into fec_candidates_88 values (new.*);
    elsif (NEW.cycle = 1986 ) then
        insert into fec_candidates_86 values (new.*);
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!';
    else
        raise exception 'Cycle (%) out of range! Fix the fec_candidates_insert_trigger() function!', NEW.cycle;
    end if;
    return null;
end;
$$
language plpgsql;

create or replace function fec_committees_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2020 ) then
        insert into fec_committees_20 values (new.*);
    elsif (NEW.cycle = 2018 ) then
        insert into fec_committees_18 values (new.*);
    elsif (NEW.cycle = 2016 ) then
        insert into fec_committees_16 values (new.*);
    elsif (NEW.cycle = 2014 ) then
        insert into fec_committees_14 values (new.*);
    elsif (NEW.cycle = 2012 ) then
        insert into fec_committees_12 values (new.*);
    elsif (NEW.cycle = 2010 ) then
        insert into fec_committees_10 values (new.*);
    elsif (NEW.cycle = 2008 ) then
        insert into fec_committees_08 values (new.*);
    elsif (NEW.cycle = 2006 ) then
        insert into fec_committees_06 values (new.*);
    elsif (NEW.cycle = 2004 ) then
        insert into fec_committees_04 values (new.*);
    elsif (NEW.cycle = 2002 ) then
        insert into fec_committees_02 values (new.*);
    elsif (NEW.cycle = 2000 ) then
        insert into fec_committees_00 values (new.*);
    elsif (NEW.cycle = 1998 ) then
        insert into fec_committees_98 values (new.*);
    elsif (NEW.cycle = 1996 ) then
        insert into fec_committees_96 values (new.*);
    elsif (NEW.cycle = 1994 ) then
        insert into fec_committees_94 values (new.*);
    elsif (NEW.cycle = 1992 ) then
        insert into fec_committees_92 values (new.*);
    elsif (NEW.cycle = 1990 ) then
        insert into fec_committees_90 values (new.*);
    elsif (NEW.cycle = 1988 ) then
        insert into fec_committees_88 values (new.*);
    elsif (NEW.cycle = 1986 ) then
        insert into fec_committees_86 values (new.*);
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!';
    else
        raise exception 'Cycle (%) out of range! Fix the fec_committees_insert_trigger() function!', NEW.cycle;
    end if;
    return null;
end;
$$
language plpgsql;

create or replace function fec_indiv_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2020 ) then
        insert into fec_indiv_20 values (new.*);
    elsif (NEW.cycle = 2018 ) then
        insert into fec_indiv_18 values (new.*);
    elsif (NEW.cycle = 2016 ) then
        insert into fec_indiv_16 values (new.*);
    elsif (NEW.cycle = 2014 ) then
        insert into fec_indiv_14 values (new.*);
    elsif (NEW.cycle = 2012 ) then
        insert into fec_indiv_12 values (new.*);
    elsif (NEW.cycle = 2010 ) then
        insert into fec_indiv_10 values (new.*);
    elsif (NEW.cycle = 2008 ) then
        insert into fec_indiv_08 values (new.*);
    elsif (NEW.cycle = 2006 ) then
        insert into fec_indiv_06 values (new.*);
    elsif (NEW.cycle = 2004 ) then
        insert into fec_indiv_04 values (new.*);
    elsif (NEW.cycle = 2002 ) then
        insert into fec_indiv_02 values (new.*);
    elsif (NEW.cycle = 2000 ) then
        insert into fec_indiv_00 values (new.*);
    elsif (NEW.cycle = 1998 ) then
        insert into fec_indiv_98 values (new.*);
    elsif (NEW.cycle = 1996 ) then
        insert into fec_indiv_96 values (new.*);
    elsif (NEW.cycle = 1994 ) then
        insert into fec_indiv_94 values (new.*);
    elsif (NEW.cycle = 1992 ) then
        insert into fec_indiv_92 values (new.*);
    elsif (NEW.cycle = 1990 ) then
        insert into fec_indiv_90 values (new.*);
    elsif (NEW.cycle = 1988 ) then
        insert into fec_indiv_88 values (new.*);
    elsif (NEW.cycle = 1986 ) then
        insert into fec_indiv_86 values (new.*);
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!';
    else
        raise exception 'Cycle (%) out of range! Fix the fec_indiv_insert_trigger() function!', NEW.cycle;
    end if;
    return null;
end;
$$
language plpgsql;

create or replace function fec_pac2cand_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2020 ) then
        insert into fec_pac2cand_20 values (new.*);
    elsif (NEW.cycle = 2018 ) then
        insert into fec_pac2cand_18 values (new.*);
    elsif (NEW.cycle = 2016 ) then
        insert into fec_pac2cand_16 values (new.*);
    elsif (NEW.cycle = 2014 ) then
        insert into fec_pac2cand_14 values (new.*);
    elsif (NEW.cycle = 2012 ) then
        insert into fec_pac2cand_12 values (new.*);
    elsif (NEW.cycle = 2010 ) then
        insert into fec_pac2cand_10 values (new.*);
    elsif (NEW.cycle = 2008 ) then
        insert into fec_pac2cand_08 values (new.*);
    elsif (NEW.cycle = 2006 ) then
        insert into fec_pac2cand_06 values (new.*);
    elsif (NEW.cycle = 2004 ) then
        insert into fec_pac2cand_04 values (new.*);
    elsif (NEW.cycle = 2002 ) then
        insert into fec_pac2cand_02 values (new.*);
    elsif (NEW.cycle = 2000 ) then
        insert into fec_pac2cand_00 values (new.*);
    elsif (NEW.cycle = 1998 ) then
        insert into fec_pac2cand_98 values (new.*);
    elsif (NEW.cycle = 1996 ) then
        insert into fec_pac2cand_96 values (new.*);
    elsif (NEW.cycle = 1994 ) then
        insert into fec_pac2cand_94 values (new.*);
    elsif (NEW.cycle = 1992 ) then
        insert into fec_pac2cand_92 values (new.*);
    elsif (NEW.cycle = 1990 ) then
        insert into fec_pac2cand_90 values (new.*);
    elsif (NEW.cycle = 1988 ) then
        insert into fec_pac2cand_88 values (new.*);
    elsif (NEW.cycle = 1986 ) then
        insert into fec_pac2cand_86 values (new.*);
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!';
    else
        raise exception 'Cycle (%) out of range! Fix the fec_pac2cand_insert_trigger() function!', NEW.cycle;
    end if;
    return null;
end;
$$
language plpgsql;

create or replace function fec_pac2pac_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2020 ) then
        insert into fec_pac2pac_20 values (new.*);
    elsif (NEW.cycle = 2018 ) then
        insert into fec_pac2pac_18 values (new.*);
    elsif (NEW.cycle = 2016 ) then
        insert into fec_pac2pac_16 values (new.*);
    elsif (NEW.cycle = 2014 ) then
        insert into fec_pac2pac_14 values (new.*);
    elsif (NEW.cycle = 2012 ) then
        insert into fec_pac2pac_12 values (new.*);
    elsif (NEW.cycle = 2010 ) then
        insert into fec_pac2pac_10 values (new.*);
    elsif (NEW.cycle = 2008 ) then
        insert into fec_pac2pac_08 values (new.*);
    elsif (NEW.cycle = 2006 ) then
        insert into fec_pac2pac_06 values (new.*);
    elsif (NEW.cycle = 2004 ) then
        insert into fec_pac2pac_04 values (new.*);
    elsif (NEW.cycle = 2002 ) then
        insert into fec_pac2pac_02 values (new.*);
    elsif (NEW.cycle = 2000 ) then
        insert into fec_pac2pac_00 values (new.*);
    elsif (NEW.cycle = 1998 ) then
        insert into fec_pac2pac_98 values (new.*);
    elsif (NEW.cycle = 1996 ) then
        insert into fec_pac2pac_96 values (new.*);
    elsif (NEW.cycle = 1994 ) then
        insert into fec_pac2pac_94 values (new.*);
    elsif (NEW.cycle = 1992 ) then
        insert into fec_pac2pac_92 values (new.*);
    elsif (NEW.cycle = 1990 ) then
        insert into fec_pac2pac_90 values (new.*);
    elsif (NEW.cycle = 1988 ) then
        insert into fec_pac2pac_88 values (new.*);
    elsif (NEW.cycle = 1986 ) then
        insert into fec_pac2pac_86 values (new.*);
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!';
    else
        raise exception 'Cycle (%) out of range! Fix the fec_pac2pac_insert_trigger() function!', NEW.cycle;
    end if;
    return null;
end;
$$
language plpgsql;

create or replace function fec_candidate_summaries_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2020 ) then
        insert into fec_candidate_summaries_20 values (new.*);
    elsif (NEW.cycle = 2018 ) then
        insert into fec_candidate_summaries_18 values (new.*);
    elsif (NEW.cycle = 2016 ) then
        insert into fec_candidate_summaries_16 values (new.*);
    elsif (NEW.cycle = 2014 ) then
        insert into fec_candidate_summaries_14 values (new.*);
    elsif (NEW.cycle = 2012 ) then
        insert into fec_candidate_summaries_12 values (new.*);
    elsif (NEW.cycle = 2010 ) then
        insert into fec_candidate_summaries_10 values (new.*);
    elsif (NEW.cycle = 2008 ) then
        insert into fec_candidate_summaries_08 values (new.*);
    elsif (NEW.cycle = 2006 ) then
        insert into fec_candidate_summaries_06 values (new.*);
    elsif (NEW.cycle = 2004 ) then
        insert into fec_candidate_summaries_04 values (new.*);
    elsif (NEW.cycle = 2002 ) then
        insert into fec_candidate_summaries_02 values (new.*);
    elsif (NEW.cycle = 2000 ) then
        insert into fec_candidate_summaries_00 values (new.*);
    elsif (NEW.cycle = 1998 ) then
        insert into fec_candidate_summaries_98 values (new.*);
    elsif (NEW.cycle = 1996 ) then
        insert into fec_candidate_summaries_96 values (new.*);
    elsif (NEW.cycle = 1994 ) then
        insert into fec_candidate_summaries_94 values (new.*);
    elsif (NEW.cycle = 1992 ) then
        insert into fec_candidate_summaries_92 values (new.*);
    elsif (NEW.cycle = 1990 ) then
        insert into fec_candidate_summaries_90 values (new.*);
    elsif (NEW.cycle = 1988 ) then
        insert into fec_candidate_summaries_88 values (new.*);
    elsif (NEW.cycle = 1986 ) then
        insert into fec_candidate_summaries_86 values (new.*);
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!';
    else
        raise exception 'Cycle (%) out of range! Fix the fec_candidate_summaries_insert_trigger() function!', NEW.cycle;
    end if;
    return null;
end;
$$
language plpgsql;

create or replace function fec_committee_summaries_insert_trigger()
returns trigger as $$
begin
    if ( NEW.cycle = 2020 ) then
        insert into fec_committee_summaries_20 values (new.*);
    elsif (NEW.cycle = 2018 ) then
        insert into fec_committee_summaries_18 values (new.*);
    elsif (NEW.cycle = 2016 ) then
        insert into fec_committee_summaries_16 values (new.*);
    elsif (NEW.cycle = 2014 ) then
        insert into fec_committee_summaries_14 values (new.*);
    elsif (NEW.cycle = 2012 ) then
        insert into fec_committee_summaries_12 values (new.*);
    elsif (NEW.cycle = 2010 ) then
        insert into fec_committee_summaries_10 values (new.*);
    elsif (NEW.cycle = 2008 ) then
        insert into fec_committee_summaries_08 values (new.*);
    elsif (NEW.cycle = 2006 ) then
        insert into fec_committee_summaries_06 values (new.*);
    elsif (NEW.cycle = 2004 ) then
        insert into fec_committee_summaries_04 values (new.*);
    elsif (NEW.cycle = 2002 ) then
        insert into fec_committee_summaries_02 values (new.*);
    elsif (NEW.cycle = 2000 ) then
        insert into fec_committee_summaries_00 values (new.*);
    elsif (NEW.cycle = 1998 ) then
        insert into fec_committee_summaries_98 values (new.*);
    elsif (NEW.cycle = 1996 ) then
        insert into fec_committee_summaries_96 values (new.*);
    elsif (NEW.cycle = 1994 ) then
        insert into fec_committee_summaries_94 values (new.*);
    elsif (NEW.cycle = 1992 ) then
        insert into fec_committee_summaries_92 values (new.*);
    elsif (NEW.cycle = 1990 ) then
        insert into fec_committee_summaries_90 values (new.*);
    elsif (NEW.cycle = 1988 ) then
        insert into fec_committee_summaries_88 values (new.*);
    elsif (NEW.cycle = 1986 ) then
        insert into fec_committee_summaries_86 values (new.*);
    elsif ( NEW.cycle is null ) then
        raise exception 'Cycle cannot be null!';
    else
        raise exception 'Cycle (%) out of range! Fix the fec_committee_summaries_insert_trigger() function!', NEW.cycle;
    end if;
    return null;
end;
$$
language plpgsql;

