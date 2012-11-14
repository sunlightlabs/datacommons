create table lobbyist_ext_ids_2008_to_2012 as
    select distinct lobbyist_ext_id from lobbying_lobbyist where year between 2008 and 2012;
