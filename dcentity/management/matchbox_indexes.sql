


create index matchbox_normalization_normalized_like on matchbox_normalization (normalized varchar_pattern_ops);

create index matchbox_normalization_original_ft on matchbox_normalization using gin(to_tsvector('datacommons', original));

create index matchbox_entityalias_alias on matchbox_entityalias (alias);
