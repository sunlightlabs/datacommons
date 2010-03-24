create unique index locations_nkey on locations(state,city,zip);

create index locations_idx_cum_freq on locations(cum_freq,state);
