from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import Import


NIMSP_TRANSACTION_NAMESPACE = 'urn:nimsp:transaction'
CRP_TRANSACTION_NAMESPACE = 'urn:fec:transaction'
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
    ('O', 'Organization')
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
    transaction_id = models.CharField(max_length=32) # <cycle>:<fec_transaction_id>, <nimsp_id>
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPES)
    filing_id = models.CharField(max_length=128, blank=True)
    is_amendment = models.BooleanField(default=False)

    # amount and date
    amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    date = models.DateField(null=True)

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
    contributor_category_order = models.CharField(max_length=3, blank=True)

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
    recipient_category_order = models.CharField(max_length=3, blank=True)

    # committee fields
    committee_name = models.CharField(max_length=255, blank=True)
    committee_ext_id = models.CharField(max_length=128, blank=True)
    committee_party = models.CharField(max_length=64, choices=PARTIES, blank=True)

    # election and seat fields
    candidacy_status = models.NullBooleanField(null=True)

    district = models.CharField(max_length=8, blank=True)
    seat = models.CharField(max_length=64, choices=SEATS, blank=True)

    district_held = models.CharField(max_length=8, blank=True)
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

