-- drop conflicting indexes
drop index lobbying_agency_agency_entity_like;
drop index lobbying_lobbyist_candidate_entity_like;
drop index lobbying_lobbyist_lobbyist_entity_like;
drop index lobbying_lobbying_client_entity_like;
drop index lobbying_lobbying_client_parent_entity_like;
drop index lobbying_lobbying_registrant_entity_like;

drop view lobbying_report;

-- MAKE THE CHANGE
alter table lobbying_agency   drop column agency_entity;
alter table lobbying_lobbyist drop column lobbyist_entity;
alter table lobbying_lobbyist drop column candidate_entity;
alter table lobbying_lobbying drop column registrant_entity;
alter table lobbying_lobbying drop column client_entity;
alter table lobbying_lobbying drop column client_parent_entity;

create view lobbying_report as
    SELECT l.transaction_id, l.transaction_type, l.transaction_type_desc, l.year, l.filing_type, l.filing_included_nsfs, l.amount, l.registrant_name, l.registrant_is_firm, l.client_name, l.client_category, l.client_ext_id, l.client_parent_name, l.include_in_industry_totals, l.use, l.affiliate,
        CASE
            WHEN (l.year % 2) = 0 THEN l.year
            ELSE l.year + 1
        END AS cycle
    FROM lobbying_lobbying l
    WHERE l.use = true
;
