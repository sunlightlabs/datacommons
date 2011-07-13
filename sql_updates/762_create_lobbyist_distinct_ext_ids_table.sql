create table lobbyist_ext_ids_2009_to_2011 as
    select distinct lobbyist_ext_id from lobbying_lobbyist where year between 2009 and 2011;
