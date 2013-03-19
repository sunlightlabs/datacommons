
-- catcodes

drop index if exists contribution_contribution_contributor_category;

create index contribution_contribution_contributor_category on contribution_contribution (contributor_category);


-- urn indexes

drop index if exists contribution_contribution_contributor_ext_id;
drop index if exists contribution_contribution_organization_ext_id;
drop index if exists contribution_contribution_parent_organization_ext_id;
drop index if exists contribution_contribution_committee_ext_id;
drop index if exists contribution_contribution_recipient_ext_id;

create index contribution_contribution_contributor_ext_id on contribution_contribution (contributor_ext_id);
create index contribution_contribution_organization_ext_id on contribution_contribution (organization_ext_id);
create index contribution_contribution_parent_organization_ext_id on contribution_contribution (parent_organization_ext_id);
create index contribution_contribution_committee_ext_id on contribution_contribution (committee_ext_id);
create index contribution_contribution_recipient_ext_id on contribution_contribution (recipient_ext_id);


-- name indexes

drop index if exists contribution_contribution_contributor_name;
drop index if exists contribution_contribution_organization_name;
drop index if exists contribution_contribution_parent_organization_name;

create index contribution_contribution_contributor_name on contribution_contribution (contributor_name);
create index contribution_contribution_organization_name on contribution_contribution (organization_name);
create index contribution_contribution_parent_organization_name on contribution_contribution (parent_organization_name);


-- case-insensitive names

drop index if exists contribution_contribution_contributor_name_lower;
drop index if exists contribution_contribution_organization_name_lower;
drop index if exists contribution_contribution_parent_organization_name_lower;
drop index if exists contribution_contribution_recipient_name_lower;

create index contribution_contribution_contributor_name_lower on contribution_contribution (lower(contributor_name));
create index contribution_contribution_organization_name_lower on contribution_contribution (lower(organization_name));
create index contribution_contribution_parent_organization_name_lower on contribution_contribution (lower(parent_organization_name));
create index contribution_contribution_recipient_name_lower on contribution_contribution (lower(recipient_name));


-- full text indexes

create text search dictionary datacommons ( template = simple, stopwords = datacommons );
create text search configuration datacommons ( copy = simple );
alter text search configuration datacommons alter mapping for asciiword with datacommons;

drop index if exists contribution_contribution_contributor_name_ft;
drop index if exists contribution_contribution_contributor_employer_ft;
drop index if exists contribution_contribution_organization_name_ft;
drop index if exists contribution_contribution_parent_organization_name_ft;
drop index if exists contribution_contribution_recipient_name_ft;

create index contribution_contribution_contributor_name_ft on contribution_contribution using gin(to_tsvector('datacommons', contributor_name));
create index contribution_contribution_contributor_employer_ft on contribution_contribution using gin(to_tsvector('datacommons', contributor_employer));
create index contribution_contribution_organization_name_ft on contribution_contribution using gin(to_tsvector('datacommons', organization_name));
create index contribution_contribution_parent_organization_name_ft on contribution_contribution using gin(to_tsvector('datacommons', parent_organization_name));
create index contribution_contribution_recipient_name_ft on contribution_contribution using gin(to_tsvector('datacommons', recipient_name));


-- other indexes

drop index if exists contribution_contribution_transaction_id;
drop index if exists contribution_contribution_transaction_namespace;
drop index if exists contribution_contribution_committee_ext_id;
drop index if exists contribution_contribution_date;
drop index if exists contribution_contribution_cycle;

create unique index contribution_contribution_transaction_id on contribution_contribution (transaction_id);
create index contribution_contribution_transaction_namespace on contribution_contribution (transaction_namespace);
create index contribution_contribution_committee_ext_id on contribution_contribution (committee_ext_id);
create index contribution_contribution_date on contribution_contribution (date);
create index contribution_contribution_cycle on contribution_contribution (cycle);

-- default sort order from API

drop index if exists contribution_contribution_defaultsort
create index contribution_contribution_defaultsort on contribution_contribution (cycle desc, amount desc);


