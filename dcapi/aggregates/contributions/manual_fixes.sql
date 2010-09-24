-- Meghan Higgins fixes to delete contributions which are not from the lobbyist M.H., as per email from Bill on 9/24/10
delete from agg_orgs_from_indiv where contributor_entity = 'b67d5c6e376d4911bb32102431a3cc33';
delete from agg_cands_from_indiv where contributor_entity = 'b67d5c6e376d4911bb32102431a3cc33' and recipient_entity = 'a00c889e30374e64b75bc3bf8095de32';

delete from agg_entities where entity_id = 'b67d5c6e376d4911bb32102431a3cc33' and cycle in (2006, 2008);
update agg_entities set contributor_count = 1, contributor_amount = 125.00 where entity_id = 'b67d5c6e376d4911bb32102431a3cc33';

delete from agg_party_from_indiv where contributor_entity = 'b67d5c6e376d4911bb32102431a3cc33' and recipient_party != 'I';
delete from agg_party_from_indiv where contributor_entity = 'b67d5c6e376d4911bb32102431a3cc33' and cycle = 2008;
update agg_party_from_indiv set count = 1, amount = 125.00 where contributor_entity = 'b67d5c6e376d4911bb32102431a3cc33';

delete from agg_contribution_sparklines where entity_id = 'b67d5c6e376d4911bb32102431a3cc33';
