-- candidate
CREATE INDEX candidate_cycle_idx ON candidate (cycle);
CREATE INDEX candidate_party_idx ON candidate (party);
-- committee
CREATE INDEX committee_cycle_idx ON committee (cycle);
CREATE INDEX committee_recip_id_idx ON committee (recip_id);
-- individual contribution
CREATE INDEX individual_cycle_idx ON individual_contribution (cycle);
CREATE INDEX individual_state_idx ON individual_contribution (state);
CREATE INDEX individual_zipcode_idx ON individual_contribution (zipcode);
CREATE INDEX individual_recip_id_idx ON individual_contribution (recip_id);
CREATE INDEX individual_org_name_idx ON individual_contribution (org_name);
-- pac to pac contribution
CREATE INDEX pac2pac_cycle_idx ON pac2pac_contribution (cycle);
CREATE INDEX pac2pac_state_idx ON pac2pac_contribution (state);
CREATE INDEX pac2pac_zipcode_idx ON pac2pac_contribution (zipcode);
CREATE INDEX pac2pac_recip_id_idx ON pac2pac_contribution (recip_id);
-- pac to candidate contribution
CREATE INDEX pac_cycle_idx ON pac_contribution (cycle);
CREATE INDEX pac_cid_idx ON pac_contribution (cid);
CREATE INDEX pac_pac_id_idx ON pac_contribution (pac_id);