CREATE TABLE locations (
   city varchar(50) not null,
   state char(2) not null,       
   zip varchar(5) not null,
   freq real default null,
   cum_freq real default null
);