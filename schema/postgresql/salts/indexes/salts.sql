CREATE INDEX salts_idx_contributionid
   ON salts(contributionid);

CREATE INDEX salts_idx_state
   ON salts(state,contributionid);