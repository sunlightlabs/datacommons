alter table matchbox_politicianmetadata add column cycle smallint check ("cycle" >= 0) not null;
alter table matchbox_politicianmetadata add column seat_status varchar(1) not null;
alter table matchbox_politicianmetadata add column seat_result varchar(1) not null;
