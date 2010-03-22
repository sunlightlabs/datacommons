from django.db import models
from matchbox.models import EntityRef


"""
FILE_TYPES = {
    "lob_issue": ('SI_ID','UniqID','IssueID','Issue','SpecIssue','Year'),
    "lob_bills": ('B_ID','SI_ID','CongNo','Bill_Name'),
}
"""

class Agency(models.Model):
    transaction_id = models.CharField(max_length=32)
    agency_name = models.CharField(max_length=255, blank=True, null=True)
    agency_entity = EntityRef('agency_transactions')
    agency_ext_id = models.CharField(max_length=128, blank=True, null=True)
    
    class Meta:
        ordering = ('agency_name',)
    
    def __unicode__(self):
        return self.agency_name

class Lobbyist(models.Model):
    year = models.IntegerField()
    transaction_id = models.CharField(max_length=32)
    lobbyist_name = models.CharField(max_length=255, blank=True, null=True)
    lobbyist_entity = EntityRef('lobbyist_transactions')
    lobbyist_ext_id = models.CharField(max_length=128, blank=True, null=True)
    candidate_entity = EntityRef('candidate_transactions')
    candidate_ext_id = models.CharField(max_length=128, blank=True, null=True)
    government_position = models.CharField(max_length=100, blank=True, null=True)
    member_of_congress = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('year','member_of_congress','lobbyist_name')
    
    def __unicode__(self):
        return u"%s is a registered lobbyist" % self.lobbyist_name
    

class Lobbying(models.Model):
    year = models.IntegerField()
    transaction_id = models.CharField(max_length=32)
    transaction_type = models.CharField(max_length=8)
    transaction_type_desc = models.CharField(max_length=128) # or do this in a lookup?
    
    filing_type = models.CharField(max_length=1)
    filing_included_nsfs = models.BooleanField(default=False)
    
    amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    
    registrant_name = models.CharField(max_length=255, blank=True, null=True)
    registrant_entity = EntityRef('registrant_transactions')
    registrant_is_firm = models.BooleanField(default=False)
    
    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_entity = EntityRef('client_transactions')
    client_category = models.CharField(max_length=8, blank=True, null=True)
    client_ext_id = models.CharField(max_length=128, blank=True, null=True)
    
    client_parent_name = models.CharField(max_length=255, blank=True, null=True)
    client_parent_entity = EntityRef('client_parent_transactions')
    
    include_in_industry_totals = models.BooleanField(default=False) # need a better name for this
    use = models.BooleanField(default=False) # CRP determines if it should be used?!
    affiliate = models.BooleanField(default=False) # what is an affiliate?!!?
    
    class Meta:
        ordering = ('year','client_name','amount','registrant_name')
        
    def __unicode__(self):
        return u"%s hired %s as a lobbyist for %0.2f" % (self.client_name or 'unknown', self.registrant_name, self.amount)