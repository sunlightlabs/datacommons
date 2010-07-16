

create index matchbox_entityalias_alias_ft on matchbox_entityalias using gin(to_tsvector('datacommons', alias));
create index matchbox_entityalias_alias_lower on matchbox_entityalias (lower(alias));
