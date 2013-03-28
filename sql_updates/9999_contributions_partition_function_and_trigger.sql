create or replace function contributions_insert_trigger()
returns trigger as $$
begin
    if ( new.cycle = 1990 and new.transaction_namespace = 'urn:nimsp:transaction' ) then
        insert into contributions_nimsp_90 values (new.*);
    elsif ( new.cycle = 1992 and new.transaction_namespace = 'urn:nimsp:transaction' ) then
        insert into contributions_nimsp_92 values (new.*);
    elsif ( new.cycle = 1994 and new.transaction_namespace = 'urn:nimsp:transaction' ) then
        insert into contributions_nimsp_94 values (new.*);
    elsif ( new.transaction_namespace = 'urn:nimsp:transaction' ) then
        insert into contributions_nimsp__out_of_range values (new.*);
    else
        insert into contributions_crp__out_of_range values (new.*);

end;
$$


language plpgsql;

--TODO: can this file be automatically generated for the script at runtime? can we introspect which years are already in the DB?
