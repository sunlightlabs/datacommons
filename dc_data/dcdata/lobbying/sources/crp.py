from dcdata.lobbying.models import Lobbying, Lobbyist, Agency

FILE_TYPES = {
    "lob_lobbying": ('Uniqid','RegistrantRaw','Registrant','IsFirm',
                     'Client_raw','Client','Ultorg','Amount','Catcode',
                     'Source','Self','IncludeNSFS','Use','Ind','Year',
                     'Type','TypeLong','OrgID','Affiliate'),
    "lob_lobbyist": ('Uniqid','Lobbyist','Lobbyist_raw','LobbyistID',
                     'Year','OfficalPos','CID','FormerCongMem'),
    "lob_agency": ('UniqID','AgencyID','Agency'),
    # "lob_indus": ('Ultorg','Client','Total','Year','Catcode'),
    # "lob_issue": ('SI_ID','UniqID','IssueID','Issue','SpecIssue','Year'),
    # "lob_bills": ('B_ID','SI_ID','CongNo','Bill_Name'),
    # "lob_rpt": ('TypeLong','Typecode'),
}

MODELS = {
    "lob_lobbying": Lobbying,
    "lob_lobbyist": Lobbyist,
    "lob_agency": Agency,
}