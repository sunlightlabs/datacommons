alter table contribution_contribution add column candidacy_status boolean;
--update contribution_contribution set candidacy_status = null where election_type = '';
--update contribution_contribution set candidacy_status = 'G' where election_type != '' and election_type != 'P';
--update contribution_contribution set candidacy_status = 'P' where election_type = 'P';
--alter table contribution_contribution drop column election_type;
