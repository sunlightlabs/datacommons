CREATE TABLE female_firstname (
  id SERIAL PRIMARY KEY,
  name VARCHAR(15) NOT NULL,
  freq REAL NOT NULL,
  cum_freq REAL NOT NULL,
  norm_cum_freq REAL NOT NULL
);