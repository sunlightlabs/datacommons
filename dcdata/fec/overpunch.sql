create or replace function overpunch(text) returns integer as $$
    select translate($1, '[{ABCDEFGHI]}JKLMNOPQR', '0012345678900123456789')::integer * case when $1 ~ ']|}|J|K|L|M|N|O|P|Q|R' then -1 else 1 end;
$$ language SQL;
