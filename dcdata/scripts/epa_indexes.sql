create index epa_echo_defendant__name_ft on epa_echo_defendant using gin(to_tsvector('datacommons', defennm));
