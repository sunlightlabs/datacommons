-- Quest Diagnostics is incorrectly listed as being the parent of Qwest Communications
update matchbox_organizationmetadata set parent_entity_id = null where entity_id = 'e8d0b02cf65b4816bca8eb8c15c0bb26';
    
-- National Education Association incorrectly listed as parent of KPAC
update matchbox_organizationmetadata set parent_entity_id = null where entity_id = 'e48f0a4f3eb8407d889db66d7b5fbf45';