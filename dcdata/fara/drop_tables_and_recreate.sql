BEGIN;
DROP TABLE IF EXISTS "fara_client_registrant";
CREATE TABLE "fara_client_registrant" (
    "id" serial NOT NULL PRIMARY KEY,
    "import_reference_id" integer NOT NULL REFERENCES "dcdata_import" ("id") DEFERRABLE INITIALLY DEFERRED,
    "client" varchar(200) NOT NULL,
    "registrant_name" varchar(200) NOT NULL,
    "terminated" varchar(20) NOT NULL,
    "location_of_client" varchar(200) NOT NULL,
    "description_of_service" text,
    "registrant_id" integer NOT NULL,
    "client_id" integer NOT NULL,
    "location_id" integer NOT NULL
)
;

DROP TABLE IF EXISTS "fara_contact";
CREATE TABLE "fara_contact" (
    "id" serial NOT NULL PRIMARY KEY,
    "import_reference_id" integer NOT NULL REFERENCES "dcdata_import" ("id") DEFERRABLE INITIALLY DEFERRED,
    "date" date,
    "date_asterisk" boolean NOT NULL,
    "contact_title" varchar(300),
    "contact_name" varchar(150),
    "contact_office" varchar(100),
    "contact_agency" varchar(100),
    "client" varchar(200) NOT NULL,
    "client_location" varchar(200) NOT NULL,
    "registrant" varchar(200) NOT NULL,
    "description" text,
    "contact_type" varchar(10) NOT NULL,
    "employees_mentioned" text,
    "affiliated_memember_bioguide_id" varchar(7),
    "source" varchar(100) NOT NULL,
    "document_id" integer,
    "registrant_id" integer NOT NULL,
    "client_id" integer NOT NULL,
    "location_id" integer NOT NULL,
    "recipient_id" integer NOT NULL,
    "record_id" integer NOT NULL
)
;

DROP TABLE IF EXISTS "fara_contribution";
CREATE TABLE "fara_contribution" (
    "id" serial NOT NULL PRIMARY KEY,
    "import_reference_id" integer NOT NULL REFERENCES "dcdata_import" ("id") DEFERRABLE INITIALLY DEFERRED,
    "date" date,
    "date_asterisk" boolean NOT NULL,
    "amount" numeric(8, 2) NOT NULL,
    "recipient" varchar(150) NOT NULL,
    "registrant" varchar(200) NOT NULL,
    "contributing_individual_or_pac" varchar(300),
    "recipient_crp_id" varchar(10),
    "recipient_bioguide_id" varchar(10),
    "source" varchar(100) NOT NULL,
    "document_id" integer,
    "registrant_id" integer NOT NULL,
    "recipient_id" integer NOT NULL,
    "record_id" integer NOT NULL
)
;

DROP TABLE IF EXISTS "fara_disbursement";
CREATE TABLE "fara_disbursement" (
    "id" serial NOT NULL PRIMARY KEY,
    "import_reference_id" integer NOT NULL REFERENCES "dcdata_import" ("id") DEFERRABLE INITIALLY DEFERRED,
    "date" date,
    "date_asterisk" boolean NOT NULL,
    "amount" numeric(12, 2) NOT NULL,
    "client" varchar(200) NOT NULL,
    "registrant" varchar(200) NOT NULL,
    "purpose" text NOT NULL,
    "to_subcontractor" varchar(200),
    "source" varchar(100) NOT NULL,
    "document_id" integer,
    "registrant_id" integer NOT NULL,
    "client_id" integer NOT NULL,
    "location_id" integer NOT NULL,
    "subcontractor_id" integer,
    "record_id" integer NOT NULL
)
;

DROP TABLE IF EXISTS "fara_payment";
CREATE TABLE "fara_payment" (
    "id" serial NOT NULL PRIMARY KEY,
    "import_reference_id" integer NOT NULL REFERENCES "dcdata_import" ("id") DEFERRABLE INITIALLY DEFERRED,
    "date" date,
    "date_asterisk" boolean NOT NULL,
    "amount" numeric(12, 2) NOT NULL,
    "client" varchar(200) NOT NULL,
    "registrant" varchar(200) NOT NULL,
    "purpose" text NOT NULL,
    "from_contractor" varchar(200),
    "source" varchar(100) NOT NULL,
    "document_id" integer,
    "registrant_id" integer NOT NULL,
    "client_id" integer NOT NULL,
    "location_id" integer NOT NULL,
    "subcontractor_id" integer,
    "record_id" integer NOT NULL
)
;
-- COMMIT;
