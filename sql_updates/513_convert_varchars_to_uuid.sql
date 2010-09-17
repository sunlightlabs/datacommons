--DROP FK's
alter TABLE "matchbox_bioguideinfo" drop constraint "matchbox_bioguideinfo_entity_id_fkey";
alter TABLE "matchbox_entityalias" drop constraint "matchbox_entityalias_entity_id_fkey";
alter TABLE "matchbox_entityattribute" drop constraint "matchbox_entityattribute_entity_id_fkey";
alter TABLE "matchbox_indivorgaffiliations" drop constraint "matchbox_indivorgaffiliations_individual_entity_id_fkey";
alter TABLE "matchbox_indivorgaffiliations" drop constraint "matchbox_indivorgaffiliations_organization_entity_id_fkey";
alter TABLE "matchbox_mergecandidate" drop constraint "matchbox_mergecandidate_entity_id_fkey";
alter TABLE "matchbox_organizationmetadata" drop constraint "matchbox_organizationmetadata_entity_id_fkey";
alter TABLE "matchbox_organizationmetadata" drop constraint "matchbox_organizationmetadata_industry_entity_id_fkey";
alter TABLE "matchbox_organizationmetadata" drop constraint "matchbox_organizationmetadata_parent_entity_id_fkey";
alter TABLE "matchbox_politicianmetadata" drop constraint "matchbox_politicianmetadata_entity_id_fkey";
alter TABLE "matchbox_sunlightinfo" drop constraint "matchbox_sunlightinfo_entity_id_fkey";
alter TABLE "matchbox_wikipediainfo" drop constraint "matchbox_wikipediainfo_entity_id_fkey";

-- drop conflicting indexes
drop index matchbox_mergecandidate_entity_id_like;
drop index matchbox_politicianmetadata_entity_id_like

-- MAKE THE CHANGE
alter table matchbox_entity               alter column id                     type uuid using id::uuid;
alter TABLE matchbox_bioguideinfo         alter column entity_id              type uuid using entity_id::uuid;
alter TABLE matchbox_entityalias          alter column entity_id              type uuid using entity_id::uuid;
alter TABLE matchbox_entityattribute      alter column entity_id              type uuid using entity_id::uuid;
alter TABLE matchbox_indivorgaffiliations alter column individual_entity_id   type uuid using individual_entity_id::uuid;
alter TABLE matchbox_indivorgaffiliations alter column organization_entity_id type uuid using organization_entity_id::uuid;
alter TABLE matchbox_mergecandidate       alter column entity_id              type uuid using entity_id::uuid;
alter TABLE matchbox_organizationmetadata alter column entity_id              type uuid using entity_id::uuid;
alter TABLE matchbox_organizationmetadata alter column industry_entity_id     type uuid using industry_entity_id::uuid;
alter TABLE matchbox_organizationmetadata alter column parent_entity_id       type uuid using parent_entity_id::uuid;
alter TABLE matchbox_politicianmetadata   alter column entity_id              type uuid using entity_id::uuid;
alter TABLE matchbox_sunlightinfo         alter column entity_id              type uuid using entity_id::uuid;
alter TABLE matchbox_wikipediainfo        alter column entity_id              type uuid using entity_id::uuid;

-- RECREATE FK's
alter TABLE "matchbox_bioguideinfo" add constraint "matchbox_bioguideinfo_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_entityalias" add constraint "matchbox_entityalias_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_entityattribute" add constraint "matchbox_entityattribute_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_indivorgaffiliations" add constraint "matchbox_indivorgaffiliations_individual_entity_id_fkey" FOREIGN KEY (individual_entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_indivorgaffiliations" add constraint "matchbox_indivorgaffiliations_organization_entity_id_fkey" FOREIGN KEY (organization_entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_mergecandidate" add constraint "matchbox_mergecandidate_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_organizationmetadata" add constraint "matchbox_organizationmetadata_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_organizationmetadata" add constraint "matchbox_organizationmetadata_industry_entity_id_fkey" FOREIGN KEY (industry_entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_organizationmetadata" add constraint "matchbox_organizationmetadata_parent_entity_id_fkey" FOREIGN KEY (parent_entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_politicianmetadata" add constraint "matchbox_politicianmetadata_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_sunlightinfo" add constraint "matchbox_sunlightinfo_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
alter TABLE "matchbox_wikipediainfo" add constraint "matchbox_wikipediainfo_entity_id_fkey" FOREIGN KEY (entity_id) REFERENCES matchbox_entity(id);
