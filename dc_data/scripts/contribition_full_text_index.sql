--create index contribution_contribution_contributor_name on contribution_contribution using gin(to_tsvector('simple', contributor_name));
create index contribution_contribution_organization_name on contribution_contribution using gin(to_tsvector('simple', organization_name));
create index contribution_contribution_parent_organization_name on contribution_contribution using gin(to_tsvector('simple', parent_organization_name));
create index contribution_contribution_committee_name on contribution_contribution using gin(to_tsvector('simple', committee_name));
create index contribution_contribution_recipient_name on contribution_contribution using gin(to_tsvector('simple', recipient_name));
