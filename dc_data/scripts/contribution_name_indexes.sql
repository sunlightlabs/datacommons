drop index if exists contribution_contribution_contributor_name_lower;
drop index if exists contribution_contribution_organization_name_lower;
drop index if exists contribution_contribution_parent_organization_name_lower;
drop index if exists contribution_contribution_committee_name_lower;
drop index if exists contribution_contribution_recipient_name_lower;

create index contribution_contribution_contributor_name_lower on contribution_contribution ((upper(contributor_name)));
create index contribution_contribution_organization_name_lower on contribution_contribution ((upper(organization_name)));
create index contribution_contribution_parent_organization_name_lower on contribution_contribution ((upper(parent_organization_name)));
create index contribution_contribution_committee_name_lower on contribution_contribution ((upper(committee_name)));
create index contribution_contribution_recipient_name_lower on contribution_contribution ((upper(recipient_name)));


create text search dictionary datacommons ( template = simple, stopwords = datacommons );
create text search configuration datacommons ( copy = simple );
alter text search configuration datacommons alter mapping for asciiword with datacommons;

drop index if exists contribution_contribution_contributor_name;
drop index if exists contribution_contribution_organization_name;
drop index if exists contribution_contribution_parent_organization_name;
drop index if exists contribution_contribution_committee_name;
drop index if exists contribution_contribution_recipient_name;

create index contribution_contribution_contributor_name on contribution_contribution using gin(to_tsvector('datacommons', contributor_name));
create index contribution_contribution_organization_name on contribution_contribution using gin(to_tsvector('datacommons', organization_name));
create index contribution_contribution_parent_organization_name on contribution_contribution using gin(to_tsvector('datacommons', parent_organization_name));
create index contribution_contribution_committee_name on contribution_contribution using gin(to_tsvector('datacommons', committee_name));
create index contribution_contribution_recipient_name on contribution_contribution using gin(to_tsvector('datacommons', recipient_name));
