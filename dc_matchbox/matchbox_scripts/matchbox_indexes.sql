


create index matchbox_normalization_normalized on matchbox_normalization (normalized);

create index matchbox_normalization_original_ft on matchbox_normalization using gin(to_tsvector('datacommons', original));

create index matchbox_entityalias_alias on matchbox_entityalias (alias);