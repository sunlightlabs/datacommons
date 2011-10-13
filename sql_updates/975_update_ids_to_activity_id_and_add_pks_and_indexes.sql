alter table epa_echo_case_identifier alter column id rename to activity_id;

alter table epa_echo_defendant rename id to activity_id;
create index epa_echo_defendant_activity_id_fk on epa_echo_defendant (activity_id);

alter table epa_echo_penalty rename id to activity_id;
create index epa_echo_penalty_activity_id_fk on epa_echo_penalty (activity_id);

alter table epa_echo_facility rename id to activity_id;
create index epa_echo_facility_activity_id_fk on epa_echo_facility (activity_id);

alter table epa_echo_milestone rename id to activity_id;
create index epa_echo_milestone_activity_id_fk on epa_echo_milestone (activity_id);
