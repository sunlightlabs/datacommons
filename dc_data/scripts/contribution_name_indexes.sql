
-- entity foreign key indexes

drop index if exists contribution_contribution_contributor_entity;
drop index if exists contribution_contribution_organization_entity;
drop index if exists contribution_contribution_parent_organization_entity;
drop index if exists contribution_contribution_committee_entity;
drop index if exists contribution_contribution_recipient_entity;

create index contribution_contribution_contributor_entity on contribution_contribution (contributor_entity);
create index contribution_contribution_organization_entity on contribution_contribution (organization_entity);
create index contribution_contribution_parent_organization_entity on contribution_contribution (parent_organization_entity);
create index contribution_contribution_committee_entity on contribution_contribution (committee_entity);
create index contribution_contribution_recipient_entity on contribution_contribution (recipient_entity);

-- urn indexes

drop index if exists contribution_contribution_contributor_urn;
drop index if exists contribution_contribution_organization_urn;
drop index if exists contribution_contribution_parent_organization_urn;
drop index if exists contribution_contribution_committee_urn;
drop index if exists contribution_contribution_recipient_urn;

create index contribution_contribution_contributor_urn on contribution_contribution (contributor_urn);
create index contribution_contribution_organization_urn on contribution_contribution (organization_urn);
create index contribution_contribution_parent_organization_urn on contribution_contribution (parent_organization_urn);
create index contribution_contribution_committee_urn on contribution_contribution (committee_urn);
create index contribution_contribution_recipient_urn on contribution_contribution (recipient_urn);


-- name indexes

drop index if exists contribution_contribution_contributor_name;
drop index if exists contribution_contribution_contributor_employer
drop index if exists contribution_contribution_organization_name;
drop index if exists contribution_contribution_parent_organization_name;
drop index if exists contribution_contribution_committee_name;
drop index if exists contribution_contribution_recipient_name;

create index contribution_contribution_contributor_name on contribution_contribution (contributor_name);
create index contribution_contribution_contributor_employer on contribution_contribution (contributor_employer);
create index contribution_contribution_organization_name on contribution_contribution (organization_name);
create index contribution_contribution_parent_organization_name on contribution_contribution (parent_organization_name);
create index contribution_contribution_committee_name on contribution_contribution (committee_name);
create index contribution_contribution_recipient_name on contribution_contribution (recipient_name);


-- full text indexes

create text search dictionary datacommons ( template = simple, stopwords = datacommons );
create text search configuration datacommons ( copy = simple );
alter text search configuration datacommons alter mapping for asciiword with datacommons;

drop index if exists contribution_contribution_contributor_name_ft;
drop index if exists contribution_contribution_contributor_employer_ft;
drop index if exists contribution_contribution_organization_name_ft;
drop index if exists contribution_contribution_parent_organization_name_ft;
drop index if exists contribution_contribution_committee_name_ft;
drop index if exists contribution_contribution_recipient_name_ft;

create index contribution_contribution_contributor_name_ft on contribution_contribution using gin(to_tsvector('datacommons', contributor_name));
create index contribution_contribution_contributor_employer_ft on contribution_contribution using gin(to_tsvector('datacommons', contributor_employer));
create index contribution_contribution_organization_name_ft on contribution_contribution using gin(to_tsvector('datacommons', organization_name));
create index contribution_contribution_parent_organization_name_ft on contribution_contribution using gin(to_tsvector('datacommons', parent_organization_name));
create index contribution_contribution_committee_name_ft on contribution_contribution using gin(to_tsvector('datacommons', committee_name));
create index contribution_contribution_recipient_name_ft on contribution_contribution using gin(to_tsvector('datacommons', recipient_name));
