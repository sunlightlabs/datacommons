CREATE TABLE navigation_bin (
    navigation_bin character varying(1) NOT NULL,
    description character varying(255) NOT NULL
);

CREATE TABLE entity_to_navigation_bin (
    entity_id uuid NOT NULL,
    navigation_bin character varying(1) NOT NULL
);

