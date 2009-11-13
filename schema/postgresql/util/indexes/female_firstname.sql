CREATE UNIQUE INDEX female_firstname_idx_name
   ON female_firstname(name);

CREATE INDEX female_firstname_idx_freq
   ON female_firstname(freq);

CREATE INDEX female_firstname_idx_cum_freq
   ON female_firstname(cum_freq);

CREATE INDEX female_firstname_idx_norm_cum_freq
   ON female_firstname(norm_cum_freq);

alter table female_firstname cluster on female_firstname_idx_norm_cum_freq;



