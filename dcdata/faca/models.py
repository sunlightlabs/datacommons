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