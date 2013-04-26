delete from matchbox_entityattribute mea using matchbox_entity me where mea.entity_id = me.id and me.type = 'industry' and mea.namespace = 'urn:fec:committee';
