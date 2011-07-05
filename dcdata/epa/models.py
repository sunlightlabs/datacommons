from django.db import models

# Create your models here.

class CaseIdentifier(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    enforcement_name = models.CharField(max_length=100, db_column='enfornm', blank=True, null=True)
    activity_type_code = models.CharField(max_length=100, db_column='acttypc', blank=True, null=True)
    activity_status_code = models.CharField(max_length=100, db_column='actsttc', blank=True, null=True)
    state_epa_flag = models.CharField(max_length=1, db_column='actsepa', blank=True, null=True) # Values: E(EPA)/S(State)
    court_docket_no = models.CharField(max_length=50, db_column='enforcd', blank=True, null=True)
    enforcement_outcome_code = models.CharField(max_length=100, db_column='enfoout', blank=True, null=True)
    hq_division = models.CharField(max_length=3, db_column='enfohqd', blank=True, null=True)
    branch = models.CharField(max_length=5, db_column='enfobrn', blank=True, null=True)
    is_voluntary_self_disclosure = models.NullBooleanField(db_column='enfovsd', blank=True, null=True)
    is_multimedia = models.NullBooleanField(db_column='actmmfl', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_case_identifier'



class Penalty(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    penalty_sought = models.IntegerField(db_column='enfops', blank=True, null=True)
    federal_penalty_accessed = models.IntegerField(db_column='enfotpa', blank=True, null=True)
    state_local_penality = models.IntegerField(db_column='enfcslp', blank=True, null=True)
    total_sep_amt = models.IntegerField(db_column='enfotsa', blank=True, null=True)
    total_comp_action = models.IntegerField(db_column='enfccaa', blank=True, null=True)
    cost_recovery_awarded_amt = models.IntegerField(db_column='enfcraa', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_penalty'



class Facility(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    facility_uin = models.CharField(max_length=12, db_column='fcltuin', blank=True, null=True)
    primary_name = models.CharField(max_length=200, db_column='fcltynm', blank=True, null=True)
    location_address = models.CharField(max_length=50, db_column='fcltyad', blank=True, null=True)
    city_name = models.CharField(max_length=50, db_column='fcltcit', blank=True, null=True)
    state_code = models.CharField(max_length=2, db_column='fcltstc', blank=True, null=True)
    zip_plus_four = models.CharField(max_length=10, db_column='fcltpst', blank=True, null=True)
    sic_codes = models.CharField(max_length=29, db_column='fclasic', blank=True, null=True)
    naics_code = models.CharField(max_length=41, db_column='fanaics', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_facility'



class Defendant(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    name = models.CharField(max_length=50, db_column='defennm', blank=True, null=True)
    is_named_in_complaint = models.NullBooleanField(db_column='defennc', blank=True, null=True)
    is_named_in_settlement = models.NullBooleanField(db_column='defenns', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_defendant'


class Milestone(models.Model):
    court_enforcement_no = models.CharField(max_length=20, db_column='enfocnu', db_index=True)
    sub_activity_type_code = models.CharField(max_length=100, db_column='subacty', blank=True, null=True)
    actual_date = models.DateField(db_column='subacad', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_milestone'


