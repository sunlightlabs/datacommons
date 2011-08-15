from django.db import models

# Create your models here.

class CaseIdentifier(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    enforcement_name = models.CharField(max_length=100, db_column='enfornm', blank=True)
    activity_type_code = models.CharField(max_length=100, db_column='acttypc', blank=True)
    activity_status_code = models.CharField(max_length=100, db_column='actsttc', blank=True)
    state_epa_flag = models.CharField(max_length=1, db_column='actsepa', blank=True) # Values: E(EPA)/S(State)
    court_docket_no = models.CharField(max_length=50, db_column='enforcd', blank=True)
    enforcement_outcome_code = models.CharField(max_length=100, db_column='enfoout', blank=True)
    hq_division = models.CharField(max_length=3, db_column='enfohqd', blank=True)
    branch = models.CharField(max_length=5, db_column='enfobrn', blank=True)
    voluntary_self_disclosure_flag = models.CharField(max_length=1, db_column='enfovsd', blank=True)
    multimedia_flag = models.CharField(max_length=1, db_column='actmmfl', blank=True)

    class Meta:
        db_table = 'epa_echo_case_identifier'



class Penalty(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    penalty_sought = models.IntegerField(db_column='enfops', blank=True, null=True)
    federal_penalty_accessed = models.IntegerField(db_column='enfotpa', blank=True, null=True)
    state_local_penality = models.IntegerField(db_column='enfcslp', blank=True, null=True)
    total_sep_amt = models.IntegerField(db_column='enfotsa', blank=True, null=True)
    total_comp_action = models.BigIntegerField(db_column='enfccaa', blank=True, null=True)
    cost_recovery_awarded_amt = models.IntegerField(db_column='enfcraa', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_penalty'



class Facility(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    facility_uin = models.BigIntegerField(db_column='fcltuin', null=True)
    primary_name = models.CharField(max_length=200, db_column='fcltynm', blank=True)
    location_address = models.CharField(max_length=50, db_column='fcltyad', blank=True)
    city_name = models.CharField(max_length=50, db_column='fcltcit', blank=True)
    state_code = models.CharField(max_length=2, db_column='fcltstc', blank=True)
    zip_plus_four = models.CharField(max_length=10, db_column='fcltpst', blank=True)
    sic_codes = models.CharField(max_length=29, db_column='fclasic', blank=True)
    naics_code = models.CharField(max_length=41, db_column='fanaics', blank=True)

    class Meta:
        db_table = 'epa_echo_facility'



class Defendant(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    name = models.CharField(max_length=50, db_column='defennm', blank=True)
    named_in_complaint_flag = models.CharField(max_length=1, db_column='defennc', blank=True)
    named_in_settlement_flag = models.CharField(max_length=1, db_column='defenns', blank=True)

    class Meta:
        db_table = 'epa_echo_defendant'


class Milestone(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    sub_activity_type_code = models.CharField(max_length=100, db_column='subacty', blank=True)
    actual_date = models.DateField(db_column='subacad', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_milestone'


