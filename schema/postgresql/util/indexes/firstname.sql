CREATE UNIQUE INDEX firstname_idx_name
   ON firstname(name);

CREATE INDEX firstname_idx_freq
   ON firstname(freq);

CREATE INDEX firstname_idx_cum_freq
   ON firstname(cum_freq);

CREATE INDEX firstname_idx_norm_cum_freq
   ON firstname(norm_cum_freq);

alter table firstname cluster on firstname_idx_norm_cum_freq;



