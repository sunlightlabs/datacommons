update agg_lobbying_registrants_for_lobbyist set registrant_name = trim(registrant_name);
update lobbying_lobbying                     set registrant_name = trim(registrant_name);
update agg_lobbying_registrants_for_client   set registrant_name = trim(registrant_name);
