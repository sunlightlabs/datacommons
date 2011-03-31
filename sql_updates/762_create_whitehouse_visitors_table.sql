create table whitehouse_visitor (
    id serial not null primary key,
    first_name varchar(64),
    middle_name varchar(64),
    last_name varchar(64)
);

insert into whitehouse_visitor (first_name, middle_name, last_name)
    select distinct first_name, middle_name, last_name from whitehouse_visitor_logs where description not ilike '%tour%' and description not ilike '%visitor%';
