from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import DataCommonsModel
from matchbox.models import EntityRef

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
    ('P','PAC'),
)

RECIPIENT_TYPES = (
    ('C','Candidate'),
    ('P','PAC'),
)

ELECTION_TYPES = (
    ('G', 'General'),
    ('P', 'Primary'),
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
    ('DEM','Democratic'),
    ('IND','Generic Independent'),
    ('REP','Republican'),
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

class Contribution(DataCommonsModel):
    
    # cycle and basic transaction fields
    cycle = models.IntegerField()
    transaction_namespace = models.CharField(max_length=64)
    transaction_id = models.CharField(max_length=32) # <cycle>:<fec_transaction_id>, <nimsp_id>
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPES)
    filing_id = models.CharField(max_length=128, blank=True, null=True)
    is_amendment = models.BooleanField(default=False)
    
    # amount and datestamp
    amount = models.IntegerField(default=0)
    datestamp = models.DateField()
    
    # contributor fields
    contributor_name = models.CharField(max_length=255, blank=True, null=True)
    contributor_urn = models.CharField(max_length=128, blank=True, null=True)
    contributor_entity = EntityRef('contributor_transactions')
    contributor_type = models.CharField(max_length=1, choices=CONTRIBUTOR_TYPES, blank=True, null=True)
    contributor_occupation = models.CharField(max_length=64, blank=True, null=True)
    contributor_employer = models.CharField(max_length=64, blank=True, null=True)
    
    contributor_gender = models.CharField(max_length=1, choices=GENDERS, default='U')
    contributor_address = models.CharField(max_length=255, blank=True, null=True)
    contributor_city = models.CharField(max_length=128, blank=True, null=True)
    contributor_state = USStateField(blank=True, null=True)
    contributor_zipcode = models.CharField(max_length=5, blank=True, null=True)
    
    contributor_category = models.CharField(max_length=8, blank=True, null=True)
    contributor_category_order = models.CharField(max_length=3, blank=True, null=True)
    
    # organization
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    organization_entity = EntityRef('organization_transactions')
    
    # parent organization
    parent_organization_name = models.CharField(max_length=255, blank=True, null=True)
    parent_organization_entity = EntityRef('parent_organization_transactions')
    
    # recipient fields
    recipient_name = models.CharField(max_length=255, blank=True, null=True)
    recipient_urn = models.CharField(max_length=128, blank=True, null=True)
    recipient_entity = EntityRef('recipient_transactions')
    recipient_party = models.CharField(max_length=64, choices=PARTIES, blank=True, null=True)
    recipient_type = models.CharField(max_length=1, choices=RECIPIENT_TYPES, blank=True, null=True)
    
    recipient_category = models.CharField(max_length=8, blank=True, null=True)
    recipient_category_order = models.CharField(max_length=3, blank=True, null=True)
    
    # committee fields
    committee_name = models.CharField(max_length=255)
    committee_urn = models.CharField(max_length=128, blank=True, null=True)
    committee_entity = EntityRef('committee_transactions')
    committee_party = models.CharField(max_length=64, choices=PARTIES, blank=True, null=True)
        
    # election and seat fields
    election_type = models.CharField(max_length=64, choices=ELECTION_TYPES, blank=True, null=True)
    district = models.CharField(max_length=8, blank=True, null=True)
    seat = models.CharField(max_length=64, choices=SEATS, blank=True, null=True)
    seat_status = models.CharField(max_length=1, choices=SEAT_STATUSES, blank=True, null=True)
    seat_result = models.CharField(max_length=1, choices=SEAT_RESULTS, blank=True, null=True)
    
    class Meta:
        ordering = ('cycle','contributor_name','amount','recipient_name')
    
    def __unicode__(self):
        return u"%s gave %i to %s" % (self.contributor or 'unknown', self.amount, self.recipient or 'unknown')

    def save(self):
        
        # check transaction type
        if self.datestamp.year < 2004 and self.transaction_type == '10levin':
            raise ValueError, "Levin funds may only occur on or after 2004"
        elif self.transaction_type == '10soft':
            raise ValueError, "Soft funds may only occur before 2004"
        
        # check employer/occupation rules
        if self.contributor_employer and not self.contributor_occupation:
            raise ValueError, "Joint employer/occupations should be saved in the contributor_occupation field"
        
        # save if all checks passed
        super(Contribution, self).save()
    
