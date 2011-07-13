
drop index if exists lobbying_lobbying_client_category;
create index lobbying_lobbying_client_category on lobbying_lobbying (client_category);

-- names
drop index if exists lobbying_lobbying_registrant_name;
drop index if exists lobbying_lobbying_client_name;
drop index if exists lobbying_lobbying_client_parent_name;
drop index if exists lobbying_lobbyist_lobbyist_name;
drop index if exists lobbying_issue_general_issue_code;

create index lobbying_lobbying_registrant_name on lobbying_lobbying (registrant_name);
create index lobbying_lobbying_client_name on lobbying_lobbying (client_name);
create index lobbying_lobbying_client_parent_name on lobbying_lobbying (client_parent_name);
create index lobbying_lobbyist_lobbyist_name on lobbying_lobbyist (lobbyist_name);
create index lobbying_issue_general_issue_code on lobbying_issue (general_issue_code);

-- case-insensitive names

drop index if exists lobbying_lobbying_registrant_name_lower;
drop index if exists lobbying_lobbying_client_name_lower;
drop index if exists lobbying_lobbying_client_parent_name_lower;
drop index if exists lobbying_lobbyist_lobbyist_name_lower;

create index lobbying_lobbying_registrant_name_lower on lobbying_lobbying (lower(registrant_name));
create index lobbying_lobbying_client_name_lower on lobbying_lobbying (lower(client_name));
create index lobbying_lobbying_client_parent_name_lower on lobbying_lobbying (lower(client_parent_name));
create index lobbying_lobbyist_lobbyist_name_lower on lobbying_lobbyist (lower(lobbyist_name));


-- names full text
drop index if exists lobbying_lobbying_registrant_name_ft;
drop index if exists lobbying_lobbying_client_name_ft;
drop index if exists lobbying_lobbying_client_parent_name_ft;
drop index if exists lobbying_lobbyist_lobbyist_name_ft;

create index lobbying_lobbying_registrant_name_ft on lobbying_lobbying using gin(to_tsvector('datacommons', registrant_name));
create index lobbying_lobbying_client_name_ft on lobbying_lobbying using gin(to_tsvector('datacommons', client_name));
create index lobbying_lobbying_client_parent_name_ft on lobbying_lobbying using gin(to_tsvector('datacommons', client_parent_name));
create index lobbying_lobbyist_lobbyist_name_ft on lobbying_lobbyist using gin(to_tsvector('datacommons', lobbyist_name));


drop index if exists lobbying_issue_specific_issue_ft;
create index lobbying_issue_specific_issue_ft on lobbying_issue using gin(to_tsvector('datacommons', specific_issue));