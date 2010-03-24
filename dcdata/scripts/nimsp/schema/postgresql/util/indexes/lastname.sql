CREATE UNIQUE INDEX lastname_idx_name
   ON lastname(name);

CREATE INDEX lastname_idx_freq
   ON lastname(freq);

CREATE INDEX lastname_idx_cum_freq
   ON lastname(cum_freq);

CREATE INDEX lastname_idx_norm_cum_freq
   ON lastname(norm_cum_freq);

alter table lastname cluster on lastname_idx_norm_cum_freq;



