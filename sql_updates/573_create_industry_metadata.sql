CREATE TABLE "matchbox_industrymetadata" (
    "id" serial NOT NULL PRIMARY KEY,
    "entity_id" uuid NOT NULL UNIQUE REFERENCES "matchbox_entity" ("id") DEFERRABLE INITIALLY DEFERRED,
    "should_show_entity" boolean NOT NULL default ('t')
)
;

