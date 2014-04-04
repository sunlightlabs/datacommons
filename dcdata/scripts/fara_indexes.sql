-- client_registrant
drop index if exists fara_client_registrant_

drop index if exists fara_client_registrant_client;
drop index if exists fara_client_registrant_registrant_name;
drop index if exists fara_client_registrant_terminated;
drop index if exists fara_client_registrant_location_of_client;
drop index if exists fara_client_registrant_description_of_service;
drop index if exists fara_client_registrant_registrant_id;
drop index if exists fara_client_registrant_client_id;
drop index if exists fara_client_registrant_location_id;

-- create index  fara_client_registrant_client                     on fara_client_registrant (client) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_client_registrant_registrant_name            on fara_client_registrant (regitrant_name) using gin(to_tsvector('datacommons', contributor_name));
create index  fara_client_registrant_terminated                 on fara_client_registrant (terminated);
-- create index  fara_client_registrant_location_of_client         on fara_client_registrant (location_of_client) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_client_registrant_description_of_service     on fara_client_registrant (description_of_service) using gin(to_tsvector('datacommons', contributor_name));
create index  fara_client_registrant_registrant_id              on fara_client_registrant (registrant_id);
create index  fara_client_registrant_client_id                  on fara_client_registrant (client_id);
create index  fara_client_registrant_location_id                on fara_client_registrant (location_id);

-- contact
drop index if exists fara_contact_date                           ;
drop index if exists fara_contact_contact_title                  ;
drop index if exists fara_contact_contact_name                   ;
drop index if exists fara_contact_contact_office                 ;
drop index if exists fara_contact_contact_agency                 ;
drop index if exists fara_contact_client                         ;
drop index if exists fara_contact_client_location                ;
drop index if exists fara_contact_registrant                     ;
drop index if exists fara_contact_description                    ;
drop index if exists fara_contact_contact_type                   ;
drop index if exists fara_contact_employees_mentioned            ;
drop index if exists fara_contact_affiliated_memember_bioguide_id;
drop index if exists fara_contact_document_id                    ;
drop index if exists fara_contact_registrant_id                  ;
drop index if exists fara_contact_client_id                      ;
drop index if exists fara_contact_location_id                    ;
drop index if exists fara_contact_recipient_id                   ;
drop index if exists fara_contact_record_id                      ;

-- create index  fara_contact_date                               on fara_contact (date);
-- create index  fara_contact_contact_title                      on fara_contact (contact_title) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_contact_contact_name                       on fara_contact (contact_name) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_contact_contact_office                     on fara_contact (contact_office) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_contact_contact_agency                     on fara_contact (contact_agency) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_contact_client                             on fara_contact (client) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_contact_client_location                    on fara_contact (client_location) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_contact_registrant                         on fara_contact (registrant) using gin(to_tsvector('datacommons', contributor_name));
-- create index  fara_contact_description                        on fara_contact (description) using gin(to_tsvector('datacommons', contributor_name));
create index  fara_contact_contact_type                       on fara_contact (contact_type);
-- create index  fara_contact_employees_mentioned                on fara_contact (employees_mentioned) using gin(to_tsvector('datacommons', contributor_name));
create index  fara_contact_affiliated_memember_bioguide_id    on fara_contact (affiliated_memember_bioguide_id);
create index  fara_contact_document_id                        on fara_contact (document_id);
create index  fara_contact_registrant_id                      on fara_contact (registrant_id);
create index  fara_contact_client_id                          on fara_contact (client_id);
create index  fara_contact_location_id                        on fara_contact (location_id);
create index  fara_contact_recipient_id                       on fara_contact (recipient_id);
create index  fara_contact_record_id                          on fara_contact (record_id);

-- fara contribution

drop index if exists fara_contribution_date                           ;
drop index if exists fara_contribution_amount                         ;
drop index if exists fara_contribution_recipient                      ;
drop index if exists fara_contribution_registrant                     ;
drop index if exists fara_contribution_contributing_individual_or_pac ;
drop index if exists fara_contribution_recipient_crp_id               ;
drop index if exists fara_contribution_recipient_bioguide_id          ;
drop index if exists fara_contribution_document_id                    ;
drop index if exists fara_contribution_registrant_id                  ;
drop index if exists fara_contribution_recipient_id                   ;
drop index if exists fara_contribution_record_id                      ;

-- create index fara_contribution_date                             on fara_contribution (date);
-- create index fara_contribution_amount                           on fara_contribution (amount);
-- create index fara_contribution_recipient                        on fara_contribution (recipient) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_contribution_registrant                       on fara_contribution (registrant) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_contribution_contributing_individual_or_pac   on fara_contribution (contributing_individual_or_pac) using gin(to_tsvector('datacommons', contributor_name));
create index fara_contribution_recipient_crp_id                 on fara_contribution (recipient_crp_id);
create index fara_contribution_recipient_bioguide_id            on fara_contribution (recipient_bioguide_id);
create index fara_contribution_document_id                      on fara_contribution (document_id);
create index fara_contribution_registrant_id                    on fara_contribution (registrant_id);
create index fara_contribution_recipient_id                     on fara_contribution (recipient_id);
create index fara_contribution_record_id                        on fara_contribution (record_id);

-- fara disbursement
drop index if exists fara_disbursement_date              ;
drop index if exists fara_disbursement_amount            ;
drop index if exists fara_disbursement_client            ;
drop index if exists fara_disbursement_registrant        ;
drop index if exists fara_disbursement_purpose           ;
drop index if exists fara_disbursement_to_subcontractor  ;
drop index if exists fara_disbursement_document_id       ;
drop index if exists fara_disbursement_registrant_id     ;
drop index if exists fara_disbursement_client_id         ;
drop index if exists fara_disbursement_location_id       ;
drop index if exists fara_disbursement_subcontractor_id  ;
drop index if exists fara_disbursement_record_id         ;

-- create index fara_disbursement_date                  on fara_disbursement (date            );
-- create index fara_disbursement_amount                on fara_disbursement (amount          );
-- create index fara_disbursement_client                on fara_disbursement (client          ) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_disbursement_registrant            on fara_disbursement (registrant      ) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_disbursement_purpose               on fara_disbursement (purpose         ) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_disbursement_to_subcontractor      on fara_disbursement (to_subcontractor) using gin(to_tsvector('datacommons', contributor_name));
create index fara_disbursement_document_id           on fara_disbursement (document_id     );
create index fara_disbursement_registrant_id         on fara_disbursement (registrant_id   );
create index fara_disbursement_client_id             on fara_disbursement (client_id       );
create index fara_disbursement_location_id           on fara_disbursement (location_id     );
create index fara_disbursement_subcontractor_id      on fara_disbursement (subcontractor_id);
create index fara_disbursement_record_id             on fara_disbursement (record_id       );


-- fara payment
drop index if exists fara_payment_date              ;
drop index if exists fara_payment_amount            ;
drop index if exists fara_payment_client            ;
drop index if exists fara_payment_registrant        ;
drop index if exists fara_payment_purpose           ;
drop index if exists fara_payment_from_subcontractor  ;
drop index if exists fara_payment_document_id       ;
drop index if exists fara_payment_registrant_id     ;
drop index if exists fara_payment_client_id         ;
drop index if exists fara_payment_location_id       ;
drop index if exists fara_payment_subcontractor_id  ;
drop index if exists fara_payment_record_id         ;

-- create index fara_payment_date                  on fara_payment (date            );
-- create index fara_payment_amount                on fara_payment (amount          );
-- create index fara_payment_client                on fara_payment (client          ) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_payment_registrant            on fara_payment (registrant      ) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_payment_purpose               on fara_payment (purpose         ) using gin(to_tsvector('datacommons', contributor_name));
-- create index fara_payment_from_subcontractor      on fara_payment (from_subcontractor) using gin(to_tsvector('datacommons', contributor_name));
create index fara_payment_document_id           on fara_payment (document_id     );
create index fara_payment_registrant_id         on fara_payment (registrant_id   );
create index fara_payment_client_id             on fara_payment (client_id       );
create index fara_payment_location_id           on fara_payment (location_id     );
create index fara_payment_subcontractor_id      on fara_payment (subcontractor_id);
create index fara_payment_record_id             on fara_payment (record_id       );
