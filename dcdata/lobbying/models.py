from django.db import models


class Lobbying(models.Model):
    transaction_id = models.CharField(max_length=64, primary_key=True, db_index=True)
    transaction_type = models.CharField(max_length=8)
    transaction_type_desc = models.CharField(max_length=128, blank=True, null=True) # or do this in a lookup?

    year = models.IntegerField()
    filing_type = models.CharField(max_length=1, blank=True, null=True)
    filing_included_nsfs = models.BooleanField(default=False)

    amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)

    registrant_name = models.CharField(max_length=255, blank=True, null=True)
    registrant_is_firm = models.BooleanField(default=False)

    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_category = models.CharField(max_length=5, blank=True, null=True)
    client_ext_id = models.CharField(max_length=128, blank=True, null=True)

    client_parent_name = models.CharField(max_length=255, blank=True, null=True)

    include_in_industry_totals = models.BooleanField(default=False) # need a better name for this
    use = models.BooleanField(default=False) # CRP determines if it should be used?!
    affiliate = models.BooleanField(default=False) # what is an affiliate?!!?

    class Meta:
        ordering = ('year','client_name','amount','registrant_name')

    def __unicode__(self):
        return u"%s hired %s as a lobbyist for %0.2f" % (self.client_name or 'unknown', self.registrant_name, self.amount)


class Agency(models.Model):
    transaction = models.ForeignKey(Lobbying, related_name='agencies')
    agency_name = models.CharField(max_length=255, blank=True, null=True)
    agency_ext_id = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        ordering = ('agency_name',)

    def __unicode__(self):
        return self.agency_name

class Lobbyist(models.Model):
    year = models.IntegerField(blank=True, null=True)
    #transaction_id = models.CharField(max_length=64, db_index=True)
    transaction = models.ForeignKey(Lobbying, related_name='lobbyists')
    lobbyist_name = models.CharField(max_length=255, blank=True, null=True)
    lobbyist_ext_id = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    candidate_ext_id = models.CharField(max_length=128, blank=True, null=True)
    government_position = models.CharField(max_length=100, blank=True, null=True)
    member_of_congress = models.BooleanField(default=False)

    class Meta:
        ordering = ('year','member_of_congress','lobbyist_name')

    def __unicode__(self):
        return u"%s is a registered lobbyist" % self.lobbyist_name

class Issue(models.Model):
    year = models.IntegerField(blank=True, null=True)
    transaction = models.ForeignKey(Lobbying, related_name='issues')
    general_issue_code = models.CharField(max_length=3)
    general_issue = models.CharField(max_length=50)
    specific_issue = models.TextField(blank=True)

    class Meta:
        ordering = ('year','transaction')

    def __unicode__(self):
        return u"%s - %s" % (self.general_issue, self.specific_issue)

class Bill(models.Model):
    bill_id = models.IntegerField(null=True)
    issue = models.ForeignKey(Issue, related_name='bills')
    congress_no = models.SmallIntegerField(null=True)
    bill_type_raw = models.CharField(max_length=12, blank=False, null=False)
    bill_type = models.CharField(max_length=2, blank=True, null=True)
    bill_no = models.SmallIntegerField(null=True)
    bill_name = models.CharField(max_length=16, null=False)

class BillTitle(models.Model):
    congress_no = models.SmallIntegerField()
    bill_type = models.CharField(max_length=2, blank=False, null=False)
    bill_no = models.SmallIntegerField(null=False)
    title = models.CharField(max_length=255)

