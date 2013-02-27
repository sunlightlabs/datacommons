create or replace function to_cycle ( date ) returns smallint as $$
    select (extract(year from $1)::smallint + (extract(year from $1)::smallint % 2))::smallint
$$ language sql;

create or replace function to_cycle ( timestamp ) returns smallint as $$
    select (extract(year from $1)::smallint + (extract(year from $1)::smallint % 2))::smallint
$$ language sql;

create or replace function to_cycle ( integer ) returns smallint as $$
    select ($1 + ($1 % 2))::smallint
$$ language sql;

create or replace function to_cycle ( smallint ) returns smallint as $$
    select $1 + ($1 % 2)::smallint
$$ language sql;
