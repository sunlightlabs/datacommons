from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import DataCommonsModel

ACTION_TYPES = (
    ('A', ''),
    ('B', ''),
    ('C', ''),
    ('D', ''),
)

RECIPIENT_TYPES = (
    ('00', ''),
    ('01', ''),
    ('02', ''),
    ('03', ''),
    ('04', ''),
    ('05', ''),
    ('06', ''),
    ('07', ''),
    ('11', ''),
    ('12', ''),
    ('20', ''),
    ('21', ''),
    ('22', ''),
    ('23', ''),
    ('25', ''),
    ('88', ''),
    ('90', ''),
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
    ('00', ''),
    ('02', ''),
    ('03', ''),
    ('04', ''),
    ('05', ''),
    ('06', ''),
    ('07', ''),
    ('08', ''),
    ('09', ''),
    ('0E', ''),
    ('10', ''),
    ('11', ''),
    ('25', ''),
    ('99', ''),
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


class Grant(DataCommonsModel):
    fiscal_year = models.IntegerField()
    flag = models.CharField(max_length=1, blank=True)
    cfda_program_number = models.CharField(max_length=8, blank=True)
    cfda_program_title = models.CharField(max_length=75, blank=True)
    state_application_id = models.CharField(max_length=20, blank=True)
    recipient_id = models.IntegerField(blank=True, null=True)
    recipient_name = models.CharField(max_length=45, blank=True)
    recipient_city = models.CharField(max_length=21, blank=True)
    recipient_city_code = models.CharField(max_length=5, blank=True)
    recipient_county = models.CharField(max_length=21, blank=True)
    recipient_county_code = models.CharField(max_length=3, blank=True)
    recipient_state = USStateField(blank=True)
    recipient_state_code = models.CharField(max_length=2, blank=True)
    recipient_zipcode = models.CharField(max_length=9, blank=True)
    recipient_country_code = models.CharField(max_length=3, blank=True)
    recipient_district = models.CharField(max_length=4, blank=True)
    recipient_type = models.CharField(max_length=2, blank=True, choices=RECIPIENT_TYPES)
    recipient_category = models.CharField(max_length=1, blank=True, choices=RECIPIENT_CATEGORIES)
    recipient_address1 = models.CharField(max_length=35, blank=True)
    recipient_address2 = models.CharField(max_length=35, blank=True)
    recipient_address3 = models.CharField(max_length=35, blank=True)
    recipient_duns = models.CharField(max_length=13, blank=True)
    recipient_parent_duns = models.CharField(max_length=13, blank=True)
    action_date = models.DateField(blank=True, null=True)
    action_type = models.CharField(max_length=1, blank=True, choices=ACTION_TYPES)
    agency_name = models.CharField(max_length=72, blank=True)
    agency_code = models.CharField(max_length=4, blank=True)
    agency_category = models.CharField(max_length=2, blank=True)
    award_id = models.IntegerField(blank=True, null=True)
    federal_award_id = models.CharField(max_length=16, blank=True)
    federal_award_mod = models.CharField(max_length=4, blank=True)
    amount_federal = models.IntegerField(blank=True, default=0)
    amount_nonfederal = models.IntegerField(blank=True, default=0)
    amount_total = models.IntegerField(blank=True, default=0)
    amount_loan = models.IntegerField(blank=True, default=0)
    amount_subsidy_cost = models.IntegerField(blank=True, default=0)
    assistance_type = models.CharField(max_length=2, blank=True, choices=ASSISTANCE_TYPES)
    assistance_category = models.CharField(max_length=1, blank=True, choices=ASSISTANCE_CATEGORIES)
    correction = models.CharField(max_length=1, blank=True, choices=CORRECTIONS)
    place_code = models.CharField(max_length=7, blank=True)
    place_state = models.USStateField(blank=True)
    place_state_code = models.CharField(max_length=2, blank=True)
    place_city = models.CharField(max_length=25, blank=True)
    place_zipcode = models.CharField(max_length=9, blank=True)
    place_district = models.CharField(max_length=2, blank=True)
    place_country_code = models.CharField(max_length=3, blank=True)
    project_description = models.CharField(max_length=125, blank=True)
    psta_agency_code = models.CharField(max_length=2, blank=True)
    psta_account_code = models.CharField(max_length=4, blank=True)
    psta_subaccount_code = models.CharField(max_length=3, blank=True)
    bfi = models.CharField(max_length=3, blank=True, choices=BFIS)
    uri = models.CharField(max_length=70, blank=True)
    
    class Meta:
        ordering = ('year','id')
    
    def __unicode__(self):
        return u"%s %s" % (self.fiscal_year, self.project_description)