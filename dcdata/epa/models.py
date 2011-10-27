from django.db import models

# Create your models here.

class CaseIdentifier(models.Model):
    activity_id = models.IntegerField(primary_key=True)
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
    activity_id = models.ForeignKey(CaseIdentifier, db_column='activity_id')
    penalty_sought = models.IntegerField(db_column='enfops', blank=True, null=True)
    federal_penalty_accessed = models.IntegerField(db_column='enfotpa', blank=True, null=True)
    state_local_penality = models.IntegerField(db_column='enfcslp', blank=True, null=True)
    total_sep_amt = models.IntegerField(db_column='enfotsa', blank=True, null=True)
    total_comp_action = models.BigIntegerField(db_column='enfccaa', blank=True, null=True)
    cost_recovery_awarded_amt = models.IntegerField(db_column='enfcraa', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_penalty'



class Facility(models.Model):
    activity_id = models.ForeignKey(CaseIdentifier, db_column='activity_id')
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
    activity_id = models.ForeignKey(CaseIdentifier, db_column='activity_id')
    name = models.CharField(max_length=50, db_column='defennm', blank=True)
    named_in_complaint_flag = models.CharField(max_length=1, db_column='defennc', blank=True)
    named_in_settlement_flag = models.CharField(max_length=1, db_column='defenns', blank=True)

    class Meta:
        db_table = 'epa_echo_defendant'


class Milestone(models.Model):
    activity_id = models.ForeignKey(CaseIdentifier, db_column='activity_id')
    sub_activity_type_code = models.CharField(max_length=100, db_column='subacty', blank=True)
    actual_date = models.DateField(db_column='subacad', blank=True, null=True)

    class Meta:
        db_table = 'epa_echo_milestone'


class DenormalizedAction(models.Model):
    case_num = models.CharField(max_length=20, primary_key=True)
    case_name = models.CharField(max_length=100)
    first_date = models.DateField(null=True)
    last_date = models.DateField(null=True)
    first_date_significance = models.CharField(max_length=64)
    last_date_significance = models.CharField(max_length=64)
    penalty = models.BigIntegerField()
    penalty_enfops = models.BigIntegerField()
    penalty_enfccaa = models.BigIntegerField()
    penalty_enfcraa = models.BigIntegerField()
    penalty_enfotpa = models.BigIntegerField()
    penalty_enfotsa = models.BigIntegerField()
    penalty_enfcslp = models.BigIntegerField()
    num_defendants = models.IntegerField()
    defendants = models.TextField()
    location_addresses = models.TextField()

    class Meta:
        db_table = 'epa_echo_actions'

