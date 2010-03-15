
from dcdata.utils.sql import *

SQL_DUMP_FILE = 'nimsp_partial_denormalization.csv'

CSV_SQL_MAPPING = [('contributionid', 'c.ContributionID', parse_int), 
                ('amount', 'c.Amount', parse_decimal), 
                ('date', 'c.Date', parse_date), 
                ('contributor', 'c.Contributor', parse_char), 
                ('newcontributor', 'c.NewContributor', parse_char), 
                ('first', 'c.First', parse_char), 
                ('last', 'c.Last', parse_char), 
                ('contributor_occupation', 'c.Occupation', parse_char), 
                ('employer', 'c.Employer', parse_char), 
                ('newemployer', 'c.NewEmployer', parse_char), 
                ('parent_organization_name', 'c.ParentCompany', parse_char), 
                ('contributorowner', 'c.ContributorOwner', parse_char), 
                ('pacname', 'c.PACName', parse_char), 
                ('address', 'c.Address', parse_char), 
                ('newaddress', 'c.NewAddress', parse_char), 
                ('contributor_city', 'c.City', parse_char), 
                ('contributor_state', 'c.State', parse_char), 
                ('contributor_zipcode', 'c.ZipCode', parse_char), 
                ('contributor_category', 'c.CatCode', parse_char), 
                ('contributor_id', 'c.NewContributorID', parse_int), 
                ('newemployerid', 'c.NewEmployerID', parse_int), 
                ('parentcompanyid', 'c.ParentCompanyID', parse_int), 
                ('unique_candidate_id', 'cand.UniqueCandidateID', parse_int),
                ('candidate_id', 'r.CandidateID', parse_int), 
                ('committee_id', 'r.CommitteeID', parse_int), 
                ('recipient_name', 'r.RecipientName', parse_char), 
                ('cycle', 'syr.Yearcode', parse_char), 
                ('seat_state', 'os.StateCode', parse_char), 
                ('district', 'os.District', parse_char), 
                ('status', 'cand.Status', parse_char), 
                ('incumbent', 'cand.ICO', parse_char), 
                ('seat', 'oc.OfficeType', parse_char), 
                ('recipient_party', 'p_cand.PartyType', parse_char), 
                ('committee_party', 'p_comm.PartyType', parse_char), 
                ('committee_name', 'comm.CommitteeName', parse_char), 
                ('contributor_industry', 'cc.IndustryCode', parse_char),
                ('recipient_state', 'r.StateCode', parse_char)]

