from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import Import
from common.db.fields.uuid_field import UUIDField
import uuid


NIMSP_TRANSACTION_NAMESPACE = 'urn:nimsp:transaction'
CRP_TRANSACTION_NAMESPACE = 'urn:fec:transaction'
DC_TRANSACTION_NAMESPACE = 'urn:dc:transaction'
UNITTEST_TRANSACTION_NAMESPACE = 'urn:unittest:transaction'


SEATS = (
    ('federal:senate', 'US Senate'),
    ('federal:house', 'US House of Representatives'),
    ('federal:president', 'US President'),
    ('state:upper', 'State Upper Chamber'),
    ('state:lower', 'State Lower Chamber'),
    ('state:governor', 'State Governor'),
)

CONTRIBUTOR_TYPES = (
    ('I','Individual'),
    ('C','Committee'),
)

RECIPIENT_TYPES = (
    ('P','Candidate'),
    ('C','Committee'),
)

TRANSACTION_TYPES = (
    ('10levin','[10] Levin Funds'),
    ('10soft','[10] Non-federal "Soft" Money'),
    ('11','[11] Tribal Contribution'),
    ('15','[15] Contribution'),
    ('15e','[15e] Earmarked Contribution'),
    ('15j','[15j] Joint Fundraising Committee'),
    ('22y','[22y] Refund'),
    ('22z','[22z] Contribution Refund To Candidate/Commitee'),
    ('24a','[24a] Independent Expenditure'),
    ('24c','[24c] Coordinated Expenditure'),
    ('24e','[24e] Independent Expenditure For Candidate'),
    ('24f','[24f] Communication Cost For Candidate'),
    ('24g','[24g] Transfer To An Affiliated Committee'),
    ('24k','[24k] Direct Contribution'),
    ('24n','[24n] Communication Cost Against Candidate'),
    ('24r','[24r] Election Recount Disbursement'),
    ('24z','[24z] In-kind Contribution'),
)

PARTIES = (
    ('3','Other'),
    ('D','Democratic'),
    ('I','Generic Independent'),
    ('L','Libertarian'),
    ('R','Republican'),
    ('U','Unkown'),
)


SEAT_STATUSES = (
    ('C','Challenger'),
    ('I','Incumbent'),
    ('O','Open'),
    ('N','Non-incumbent'),
)

SEAT_RESULTS = (
    ('L','Loss'),
    ('W','Win'),
)

GENDERS = (
    ('F','Female'),
    ('M','Male'),
    ('U','Unknown'),
)

class Contribution(models.Model):
    import_reference = models.ForeignKey(Import)

    # cycle and basic transaction fields
    cycle = models.IntegerField()
    transaction_namespace = models.CharField(max_length=64)
    transaction_id = models.CharField(max_length=64) # <cycle>:<fec_transaction_id>, <nimsp_id>
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPES)
    filing_id = models.CharField(max_length=128, blank=True)
    is_amendment = models.BooleanField(default=False)

    # amount and date
    amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    date = models.DateField(null=True, db_index=True)

    # contributor fields
    contributor_name = models.CharField(max_length=255, blank=True)
    contributor_ext_id = models.CharField(max_length=128, blank=True)
    contributor_type = models.CharField(max_length=1, choices=CONTRIBUTOR_TYPES, blank=True)
    contributor_occupation = models.CharField(max_length=64, blank=True)
    contributor_employer = models.CharField(max_length=64, blank=True)

    contributor_gender = models.CharField(max_length=1, choices=GENDERS, default='U')
    contributor_address = models.CharField(max_length=255, blank=True)
    contributor_city = models.CharField(max_length=128, blank=True)
    contributor_state = USStateField(blank=True)
    contributor_zipcode = models.CharField(max_length=5, blank=True)

    contributor_category = models.CharField(max_length=8, blank=True)

    # organization
    organization_name = models.CharField(max_length=255, blank=True)
    organization_ext_id = models.CharField(max_length=128, blank=True)

    # parent organization
    parent_organization_name = models.CharField(max_length=255, blank=True)
    parent_organization_ext_id =  models.CharField(max_length=128, blank=True)

    # recipient fields
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_ext_id = models.CharField(max_length=128, blank=True)
    recipient_party = models.CharField(max_length=64, choices=PARTIES, blank=True)
    recipient_type = models.CharField(max_length=1, choices=RECIPIENT_TYPES, blank=True)
    recipient_state = USStateField(blank=True)
    recipient_state_held = USStateField(blank=True)

    recipient_category = models.CharField(max_length=8, blank=True)

    # committee fields
    committee_name = models.CharField(max_length=255, blank=True)
    committee_ext_id = models.CharField(max_length=128, blank=True)
    committee_party = models.CharField(max_length=64, choices=PARTIES, blank=True)

    # election and seat fields
    candidacy_status = models.NullBooleanField(null=True)

    district = models.CharField(max_length=8, blank=True)
    district_held = models.CharField(max_length=8, blank=True)

    seat = models.CharField(max_length=64, choices=SEATS, blank=True)
    seat_held = models.CharField(max_length=64, choices=SEATS, blank=True)

    seat_status = models.CharField(max_length=1, choices=SEAT_STATUSES, blank=True)
    seat_result = models.CharField(max_length=1, choices=SEAT_RESULTS, blank=True)

    class Meta:
        ordering = ('cycle','contributor_name','amount','recipient_name')

    def __unicode__(self):
        return u"%s gave %i to %s" % (self.contributor_name or 'unknown', self.amount, self.recipient_name or 'unknown')

    def save(self, **kwargs):

        if self.transaction_namespace == NIMSP_TRANSACTION_NAMESPACE:
            pass
        elif self.transaction_namespace == UNITTEST_TRANSACTION_NAMESPACE:
            pass
        elif self.transaction_namespace == CRP_TRANSACTION_NAMESPACE:
            # check transaction type
            if self.date:
                if self.date.year < 2004 and self.transaction_type == '10levin':
                    raise ValueError, "Levin funds may only occur on or after 2004"
                elif self.transaction_type == '10soft':
                    raise ValueError, "Soft funds may only occur before 2004"
        else:
            raise ValueError, "Unhandled transaction_namespace (%s)" % (self.transaction_namespace or 'None')

        if len(self.contributor_gender) > 1:
            raise ValueError, 'Gender of %s is not valid' % self.contributor_gender

        if self.contributor_state and len(self.contributor_state) > 2:
            raise ValueError, "State '%s' is not a valid state." % self.contributor_state

        if self.date and self.date.year < 1900:
            raise ValueError, 'Year %s is not a valid year. Must use 4-digit years.' % self.date.year

        # save if all checks passed
        super(Contribution, self).save(**kwargs)


class ContributionDC(models.Model):
    transaction_id = UUIDField(primary_key=True, auto=True, default=uuid.uuid4().hex)
    transaction_namespace = models.CharField(max_length=64)
    recipient_name = models.CharField(max_length=32)
    committee_name = models.CharField(max_length=100)
    contributor_name = models.CharField(max_length=100)
    contributor_entity = UUIDField(null=True)
    contributor_type = models.CharField(max_length=24)
    contributor_type_internal = models.CharField(max_length=12)
    payment_type = models.CharField(max_length=42, null=True)
    contributor_address = models.CharField(max_length=40, null=True)
    contributor_city = models.CharField(max_length=20, null=True)
    contributor_state = models.CharField(max_length=2, null=True)
    contributor_zipcode = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    recipient_party = models.CharField(max_length=3)
    recipient_state = models.CharField(max_length=3)
    seat = models.CharField(max_length=64, choices=SEATS, blank=True)
    ward = models.IntegerField()

    class Meta:
        db_table = 'contribution_dc'
        managed = False


class Bundle(models.Model):
    file_num = models.IntegerField(primary_key=True) # FILE_NUM
    committee_fec_id = models.CharField(max_length=9) # CMTE_ID
    committee_name = models.CharField(max_length=255) # CMTE_NM
    report_year = models.SmallIntegerField() # RPT_YR
    report_type = models.CharField(max_length=3) # RPT_TP
    is_amendment = models.BooleanField() #AMNDT_IND Values in file: (N)ew/(A)mendment
    report_type_description = models.CharField(max_length=255) # RPT_TP_DESC
    start_date = models.DateField(null=True) # CVG_START_DT
    end_date = models.DateField(null=True) # CVG_END_DT
    reporting_period_amount = models.IntegerField(null=True) # QTR_MON_BUNDLED_CONTB
    semi_annual_amount = models.IntegerField(null=True) # SEMI_AN_BUNDLED_CONTB
    filing_date = models.DateField(null=True) # RECEIPT_DT
    first_image_num = models.BigIntegerField() # BEGIN_IMAGE_NUM: the first "page number" in FEC's document ID's
    pdf_url = models.URLField()

    should_ignore = models.NullBooleanField(null=True) # our field: three-valued boolean

# This is a straight import of the CRP committee table.
# We're primarily intersted in the mapping from committee IDs to candidate IDs.
# command to reload the table is:
#   \copy contribution_committee (cycle, committee_id, short_name, sponsor, organization_name, recipient_id, recipient_code, fec_candidate_id, party, category, category_source, sensitive, "foreign", active) from cmtes10.txt csv quote '|' force not null party, organization_name, recipient_code, category, category_source, sensitive, short_name

class Committee(models.Model):
    cycle = models.IntegerField()
    committee_id = models.CharField(max_length=9)
    short_name = models.CharField(max_length=40)
    sponsor = models.CharField(max_length=40, null=True)
    organization_name = models.CharField(max_length=40)
    recipient_id = models.CharField(max_length=9)
    recipient_code = models.CharField(max_length=2)
    fec_candidate_id = models.CharField(max_length=9)
    party = models.CharField(max_length=1)
    category = models.CharField(max_length=5)
    category_source = models.CharField(max_length=40)
    sensitive = models.CharField(max_length=1)
    foreign = models.IntegerField()
    active = models.IntegerField()
    



class LobbyistBundle(models.Model):
    file_num = models.ForeignKey('Bundle', db_column='file_num') # FILE_NUM

    """
    following are fields in the worksheet which duplicate the BundledContribution fields
    """
    #committee_fec_id = models.CharField(max_length=9) # CMTE_ID
    #committee_name = models.CharField(max_length=255) # CMTE_NM
    #report_year = models.SmallIntegerField() # RPT_YR
    #report_type = models.CharField(max_length=3) # RPT_TP
    #is_amendment = models.BooleanField() #AMNDT_IND Values in file: (N)ew/(A)mendment
    #start_date = models.DateField() # CVG_START_DT
    #end_date = models.DateField() # CVG_END_DT

    image_num = models.BigIntegerField() # IMAGE_NUM: the FEC's actual document ID
    contributor_fec_id = models.CharField(max_length=9, null=True) # CONTBR_ID
    name = models.CharField(max_length=255) # CONTBR_NM
    street_addr1 = models.CharField(max_length=255, null=True) # CONTBR_ST1
    street_addr2 = models.CharField(max_length=255, null=True) # CONTBR_ST2
    city = models.CharField(max_length=255, null=True) # CONTBR_CITY
    state = models.CharField(max_length=2, null=True) # CONTBR_ST
    zip_code = models.CharField(max_length=10, null=True) # CONTBR_ZIP
    employer = models.CharField(max_length=255, null=True) # CONTBR_EMPLOYER
    occupation = models.CharField(max_length=255, null=True) # CONTBR_OCCUPATION
    amount = models.IntegerField(null=True) # CONTB_RECEIPT_AMT
    semi_annual_amount = models.IntegerField(null=True) # CONTB_AGGREGATE_YTD

    # reporting_period_amount
    # semi_annual_amount

    receipt_type = models.CharField(max_length=3, null=True)



class LobbyistBundlingDenormalized(models.Model):
    """ This class is intended for use in TD """
    file_num = models.IntegerField(primary_key=True) # FILE_NUM
    committee_name = models.CharField(max_length=255) # CMTE_NM
    committee_fec_id = models.CharField(max_length=9) # CMTE_ID
    report_year = models.SmallIntegerField() # RPT_YR
    report_type = models.CharField(max_length=3) # RPT_TP
    start_date = models.DateField(null=True) # CVG_START_DT
    end_date = models.DateField(null=True) # CVG_END_DT
    period_amount = models.IntegerField(null=True) # CONTB_RECEIPT_AMT
    semi_annual_amount = models.IntegerField(null=True) # CONTB_AGGREGATE_YTD
    standardized_recipient_name = models.CharField(max_length=255)
    standardized_lobbyist_name = models.CharField(max_length=255) # CONTBR_NM
    standardized_firm_name = models.CharField(max_length=255, null=True) # CONTBR_EMPLOYER
    bundler_name = models.CharField(max_length=255)
    bundler_employer = models.CharField(max_length=255)
    bundler_occupation = models.CharField(max_length=255)
    bundler_fec_id = models.CharField(max_length=9, null=True) # CONTBR_ID
    street_addr1 = models.CharField(max_length=255) # CONTBR_ST1
    street_addr2 = models.CharField(max_length=255, null=True) # CONTBR_ST2
    city = models.CharField(max_length=255) # CONTBR_CITY
    state = models.CharField(max_length=2) # CONTBR_ST
    zip_code = models.CharField(max_length=10) # CONTBR_ZIP
    pdf_url = models.URLField()

    class Meta:
        managed = False
        db_table = 'lobbyist_bundling_denormalized_view'

