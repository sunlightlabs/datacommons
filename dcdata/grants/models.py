from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import Import

RECORD_TYPES = (
    ('1', "County aggregate reporting"),
    ('2', "Action-by-action reporting"),
)

ACTION_TYPES = (
    ('A', 'New assistance action'),
    ('B', 'Continuation'),
    ('C', 'Revision'),
    ('D', 'Funding adjustment to completed project'),
)

RECIPIENT_TYPES = (
    ('00', 'State government'),
    ('01', 'County government'),
    ('02', 'City or township government'),
    ('03', '03'),
    ('04', 'Special district government'),
    ('05', 'Independent school district'),
    ('06', 'State controlled institution of higher education'),
    ('07', '07'),
    ('11', 'Indian tribe'),
    ('12', 'Other nonprofit'),
    ('20', 'Private higher education'),
    ('21', 'individual'),
    ('22', 'Profit organization'),
    ('23', 'Small business'),
    ('25', 'Other'),
    ('88', '88'),
    ('90', '90'),
)

RECIPIENT_CATEGORIES = (
    ('f', 'For Profit'),
    ('g', 'Government'),
    ('h', 'Higher Education'),
    ('i', 'Individual'),
    ('n', 'Nonprofit'),
    ('o', 'Other'),
)

ASSISTANCE_TYPES = (
    ('00', '00'),
    ('02', 'Block grant (A)'),
    ('03', 'Formula grant (A)'),
    ('04', 'Project grant (B)'),
    ('05', 'Cooperative agreement (B)'),
    ('06', 'Direct payment for specified use, as a subsidy or other non-reimbursable direct financial aid (C)'),
    ('07', 'Direct loan (D)'),
    ('08', 'Guaranteed/insured loan (F)'),
    ('09', 'Insurance (G)'),
    ('0E', '0E'),
    ('10', 'Direct payment with unrestricted use (D)'),
    ('11', 'Other reimbursable, contingent, intangible or indirect financial assistance'),
    ('25', '25'),
    ('99', '99'),
)

ASSISTANCE_CATEGORIES = (
    ('d', 'Direct Payments'),
    ('g', 'Grants and Cooperative Agreements'),
    ('i', 'Insurance'),
    ('l', 'Loans'),
    ('o', 'Other'),
)

CORRECTIONS = (
    ('0', ''),
    ('2', ''),
    ('5', ''),
    ('6', ''),
    ('B', ''),
    ('C', ''),
    ('F', ''),
    ('L', ''),
    ('_', ''),
)

BFIS = (
    ('000', ''),
    ('0NO', ''),
    ('NON', ''),
    ('REC', ''),
)

AGENCY_CATEGORIES = (
    ('12', ''),
    ('13', ''),
    ('14', ''),
    ('15', ''),
    ('16', ''),
    ('19', ''),
    ('20', ''),
    ('24', ''),
    ('28', ''),
    ('31', ''),
    ('36', ''),
    ('49', ''),
    ('68', ''),
    ('69', ''),
    ('70', ''),
    ('72', ''),
    ('73', ''),
    ('75', ''),
    ('80', ''),
    ('86', ''),
    ('89', ''),
    ('91', ''),
    ('97', ''),
    ('ot', ''),
)


class Grant(models.Model):
    imported_on = models.DateField(auto_now_add=True)
    
    fiscal_year = models.IntegerField()
    record_type = models.CharField(max_length=1, blank=True, choices=RECORD_TYPES)
    rec_flag = models.NullBooleanField(blank=True)
    cfda_program_num = models.CharField(max_length=8, blank=True)
    cfda_program_title = models.CharField(max_length=255, blank=True)
    sai_number = models.CharField(max_length=20, blank=True)
    account_title = models.CharField(max_length=100, blank=True)
    recipient_name = models.CharField(max_length=45, blank=True)
    recipient_city_name = models.CharField(max_length=21, blank=True)
    recipient_city_code = models.CharField(max_length=5, blank=True)
    recipient_county_name = models.CharField(max_length=21, blank=True)
    recipient_county_code = models.CharField(max_length=3, blank=True)
    recipient_state_code = USStateField(blank=True)
    recipient_zip = models.CharField(max_length=9, blank=True)
    recipient_country_code = models.CharField(max_length=3, blank=True)
    recipient_cd = models.CharField(max_length=4, blank=True)
    recipient_type = models.CharField(max_length=2, blank=True, choices=RECIPIENT_TYPES)
    recip_cat_type = models.CharField(max_length=1, blank=True, choices=RECIPIENT_CATEGORIES)
    receip_addr1 = models.CharField(max_length=35, blank=True)
    receip_addr2 = models.CharField(max_length=35, blank=True)
    receip_addr3 = models.CharField(max_length=35, blank=True)
    duns_no = models.CharField(max_length=13, blank=True)
    obligation_action_date = models.DateField(blank=True, null=True)
    action_type = models.CharField(max_length=1, blank=True, choices=ACTION_TYPES)
    agency_name = models.CharField(max_length=72, blank=True)
    agency_code = models.CharField(max_length=4, blank=True)
    maj_agency_cat = models.CharField(max_length=2, blank=True)
    federal_award_id = models.CharField(max_length=16, blank=True)
    federal_award_mod = models.CharField(max_length=4, blank=True)
    fed_funding_amount = models.BigIntegerField(blank=True, default=0)
    non_fed_funding_amount = models.BigIntegerField(blank=True, default=0)
    total_funding_amount = models.BigIntegerField(blank=True, default=0)
    face_loan_guran = models.BigIntegerField(blank=True, default=0)
    orig_sub_guran = models.BigIntegerField(blank=True, default=0)
    assistance_type = models.CharField(max_length=2, blank=True, choices=ASSISTANCE_TYPES)
    asst_cat_type = models.CharField(max_length=1, blank=True, choices=ASSISTANCE_CATEGORIES)
    correction_late_ind = models.CharField(max_length=1, blank=True, choices=CORRECTIONS)
    principal_place_code = models.CharField(max_length=7, blank=True)
    principal_place_state = models.CharField(max_length=64, blank=True)
    principal_place_state_code = USStateField(blank=True)
    principal_place_cc = models.CharField(max_length=25, blank=True)
    principal_place_zip = models.CharField(max_length=9, blank=True)
    principal_place_cd = models.CharField(max_length=4, blank=True)
    project_description = models.CharField(max_length=255, blank=True)
    progsrc_agen_code = models.CharField(max_length=2, blank=True)
    progsrc_acnt_code = models.CharField(max_length=4, blank=True)
    progsrc_subacnt_code = models.CharField(max_length=3, blank=True)
    uri = models.CharField(max_length=70, blank=True)
    duns_conf_code = models.CharField(max_length=2, blank=True)
    ending_date = models.DateField(blank=True, null=True)
    fyq = models.CharField(max_length=10, blank=True)
    fyq_correction = models.CharField(max_length=5, blank=True)
    starting_date = models.DateField(blank=True, null=True)
    transaction_status = models.CharField(max_length=32, blank=True)
    unique_transaction_id = models.CharField(max_length=32, blank=True)
    
    class Meta:
        ordering = ('fiscal_year','id')
    
    def __unicode__(self):
        return u"%s %s" % (self.fiscal_year, self.project_description)
