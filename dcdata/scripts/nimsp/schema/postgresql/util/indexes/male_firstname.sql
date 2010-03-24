CREATE UNIQUE INDEX male_firstname_idx_name
   ON male_firstname(name);

CREATE INDEX male_firstname_idx_freq
   ON male_firstname(freq);

CREATE INDEX male_firstname_idx_cum_freq
   ON male_firstname(cum_freq);

CREATE INDEX male_firstname_idx_norm_cum_freq
   ON male_firstname(norm_cum_freq);

alter table male_firstname cluster on male_firstname_idx_norm_cum_freq;
