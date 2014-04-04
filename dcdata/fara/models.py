from django.db import models
from dcdata.models import Import


class ClientRegistrant(models.Model):
    import_reference = models.ForeignKey(Import, related_name="fara_client_registrant")
    client = models.CharField(max_length=200)
    registrant_name = models.CharField(max_length=200)
    terminated = models.CharField(max_length=20)
    location_of_client = models.CharField(max_length=200)
    description_of_service = models.TextField(null=True)
    registrant_id = models.IntegerField()
    client_id = models.IntegerField()
    location_id = models.IntegerField()
    FIELDNAMES = ('client',
                  'registrant_name',
                  'terminated',
                  'location_of_client',
                  'description_of_service',
                  'registrant_id',
                  'client_id',
                  'location_id')

    class Meta:
        db_table = 'fara_client_registrant'
        managed = False


class Contact(models.Model):
    import_reference = models.ForeignKey(Import, related_name="fara_contact")
    date = models.DateField(null=True)
    date_asterisk = models.BooleanField(default=False)
    contact_title = models.CharField(max_length=300, null=True)
    contact_name = models.CharField(max_length=150, null=True)
    contact_office = models.CharField(max_length=100, null=True)
    contact_agency = models.CharField(max_length=100, null=True)
    client = models.CharField(max_length=200)
    client_location = models.CharField(max_length=200)
    registrant = models.CharField(max_length=200)
    description = models.TextField(null=True)
    contact_type = models.CharField(max_length=10)
    employees_mentioned = models.TextField(null=True)
    affiliated_memember_bioguide_id = models.CharField(max_length=7, null=True)
    source = models.CharField(max_length=100)
    document_id = models.IntegerField(null=True)
    registrant_id = models.IntegerField()
    client_id = models.IntegerField()
    location_id = models.IntegerField()
    recipient_id = models.IntegerField()
    record_id = models.IntegerField()
    FIELDNAMES = (
                    'date',
                    'contact_title',
                    'contact_name',
                    'contact_office',
                    'contact_agency',
                    'client',
                    'client_location',
                    'registrant',
                    'description',
                    'contact_type',
                    'employees_mentioned',
                    'affiliated_memember_bioguide_id',
                    'source',
                    'document_id',
                    'registrant_id',
                    'client_id',
                    'location_id',
                    'recipient_id',
                    'record_id'
        )

    class Meta:
        db_table = 'fara_contact'
        managed = False


class Contribution(models.Model):
    import_reference = models.ForeignKey(Import, related_name="fara_contribution")
    date = models.DateField(null=True)
    date_asterisk = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    recipient = models.CharField(max_length=150)
    registrant = models.CharField(max_length=200)
    contributing_individual_or_pac = models.CharField(max_length=300, null=True)
    recipient_crp_id = models.CharField(max_length=10, null=True)
    recipient_bioguide_id = models.CharField(max_length=10, null=True)
    source = models.CharField(max_length=100)
    document_id = models.IntegerField(null=True)
    registrant_id = models.IntegerField()
    recipient_id = models.IntegerField()
    record_id = models.IntegerField()
    FIELDNAMES = (
        'date',
        'amount',
        'recipient',
        'registrant',
        'contributing_individual_or_pac',
        'recipient_crp_id',
        'recipient_bioguide_id',
        'source',
        'document_id',
        'registrant_id',
        'recipient_id',
        'record_id'
    )

    class Meta:
        db_table = 'fara_contribution'
        managed = False


class Disbursement(models.Model):
    import_reference = models.ForeignKey(Import, related_name="fara_disbursement")
    date = models.DateField(null=True)
    date_asterisk = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    client = models.CharField(max_length=200)
    registrant = models.CharField(max_length=200)
    purpose = models.TextField()
    to_subcontractor = models.CharField(max_length=200, null=True)
    source = models.CharField(max_length=100)
    document_id = models.IntegerField(null=True)
    registrant_id = models.IntegerField()
    client_id = models.IntegerField()
    location_id = models.IntegerField()
    subcontractor_id = models.IntegerField(null=True)
    record_id = models.IntegerField()
    FIELDNAMES = (
        'date',
        'amount',
        'client',
        'registrant',
        'purpose',
        'to_subcontractor',
        'source',
        'document_id',
        'registrant_id',
        'client_id',
        'location_id',
        'subcontractor_id',
        'record_id'
    )


    class Meta:
        db_table = 'fara_disbursement'
        managed = False


class Payment(models.Model):
    import_reference = models.ForeignKey(Import, related_name="fara_payment")
    date = models.DateField(null=True)
    date_asterisk = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    client = models.CharField(max_length=200)
    registrant = models.CharField(max_length=200)
    purpose = models.TextField()
    from_contractor = models.CharField(max_length=200, null=True)
    source = models.CharField(max_length=100)
    document_id = models.IntegerField(null=True)
    registrant_id = models.IntegerField()
    client_id = models.IntegerField()
    location_id = models.IntegerField()
    subcontractor_id = models.IntegerField(null=True)
    record_id = models.IntegerField()
    FIELDNAMES = (
        'date',
        'amount',
        'client',
        'registrant',
        'purpose',
        'from_contractor',
        'source',
        'document_id',
        'registrant_id',
        'client_id',
        'location_id',
        'subcontractor_id',
        'record_id'
    )

    class Meta:
        db_table = 'fara_payment'
        managed = False
