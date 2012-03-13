from django.db import models
from common.db.fields.uuid_field import UUIDField


class FACARecord(models.Model):

    agency_abbr = models.CharField(max_length=12)
    agency_name = models.CharField(max_length=400)
    committee_name = models.CharField(max_length=510)
    committee_url = models.CharField(max_length=255)
    member_name = models.CharField(max_length=100)
    member_firstlast = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=510)
    chair = models.BooleanField()
    org_name = models.CharField(max_length=255, null=True)
    org_id = UUIDField(null=True)
    appointment_type = models.CharField(max_length=100)
    appointment_term = models.CharField(max_length=100)
    pay_plan = models.CharField(max_length=140)
    pay_source = models.CharField(max_length=100)
    member_designation = models.CharField(max_length=100)
    represented_group = models.CharField(max_length=508)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    class Meta:
        db_table = "faca_records"


class FACAMember(models.Model):
    membersid = models.BigIntegerField(primary_key=True)
    cid = models.BigIntegerField()
    cno = models.BigIntegerField()
    fy = models.CharField(max_length=8)
    prefix = models.CharField(max_length=20)
    firstname = models.CharField(max_length=30)
    middlename = models.CharField(max_length=30)
    lastname = models.CharField(max_length=40)
    suffix = models.CharField(max_length=20)
    chairperson = models.CharField(max_length=6)
    occupationoraffiliation = models.CharField(max_length=510)
    startdate = models.CharField(max_length=100)
    enddate = models.CharField(max_length=100)
    appointmenttype = models.CharField(max_length=100)
    appointmentterm = models.CharField(max_length=100)
    payplan = models.CharField(max_length=140)
    paysource = models.CharField(max_length=100)
    memberdesignation = models.CharField(max_length=100)
    representedgroup = models.CharField(max_length=508)

    class Meta:
        db_table = "faca_members"

    def _build_name(self):
        # leaving suffix off of the full name for now, because
        # this messes up NameCleaver, because the suffixes
        # in this dataset seem to be mostly degrees, like "PhD, RN", or "MA"
        return ' '.join([ x for x in [self.firstname.strip(), self.middlename.strip(), self.lastname.strip().replace(',', '')] if x])

    name = property(_build_name)


class FACANormalizedMember(models.Model):
    firstname = models.CharField(max_length=30)
    middlename = models.CharField(max_length=30)
    lastname = models.CharField(max_length=40)
    suffix = models.CharField(max_length=20)
    occupationoraffiliation = models.CharField(max_length=510)

    class Meta:
        db_table = "tmp_akr_faca_members_normalized"

    def _build_name(self):
        # leaving suffix off of the full name for now, because
        # this messes up NameCleaver, because the suffixes
        # in this dataset seem to be mostly degrees, like "PhD, RN", or "MA"
        return ' '.join([ x for x in [self.firstname, self.middlename, self.lastname] if x])

    name = property(_build_name)
