from django.db import models
from dcdata.models import Import


class ClientRegistrant(models.Model):
    import_reference = models.ForeignKey(Import)
    client = models.CharField(max_length=200)
    registrant_name = models.CharField(max_length=200)
    terminated = models.CharField(max_length=20)
    location_of_client = models.CharField(max_length=200)
    description_of_service = models.TextField(null=True)
    registrant_id = models.IntegerField()
    client_id = models.IntegerField()
    location_id = models.IntegerField()
    FIELD_MAP = {
        'Client':                                   'client',
        'Registrant name':                          'registrant_name',
        'Terminated':                               'terminated',
        'Location of Client':                       'location_of_client',
        'Description of service (when available)':  'description_of_service',
        'Registrant ID':                            'registrant_id',
        'Client ID':                                'client_id',
        'Location ID':                              'location_id'}

    class Meta:
        db_table = 'fara_client_registrant'
        managed = False


class Contact(models.Model):
    import_reference = models.ForeignKey(Import)
    date = models.CharField(max_length=20)
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
    FIELD_MAP = {
        'Date':                          'date',
        'Contact Title':                 'contact_title',
        'Contact Name':                  'contact_name',
        'Contact Office':                'contact_office',
        'Contact Agency':                'contact_agency',
        'Client':                        'client',
        'Client Location':               'client_location',
        'Registrant':                    'registrant',
        'Description':                   'description',
        'Type':                          'contact_type',
        'Employees Mentioned':           'employees_mentioned',
        'Affiliated Member Bioguide ID': 'affiliated_memember_bioguide_id',
        'Source':                        'source',
        'Document ID':                   'document_id',
        'Registrant ID':                 'registrant_id',
        'Client ID':                     'client_id',
        'Location ID':                   'location_id',
        'Recipient ID':                  'recipient_id',
        'Record ID':                     'record_id'
    }

    class Meta:
        db_table = 'fara_contact'
        managed = False


class Contribution(models.Model):
    import_reference = models.ForeignKey(Import)
    date = models.CharField(max_length=15)
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
    FIELD_MAP = {
        'Date':                             'date',
        'Amount':                           'amount',
        'Recipient':                        'recipient',
        'Registrant':                       'registrant',
        'Contributing Individual or PAC':   'contributing_individual_or_pac',
        'CRP ID of Recipient':              'recipient_crp_id',
        'Bioguide ID':                      'recipient_bioguide_id',
        'Source':                           'source',
        'Document ID':                      'document_id',
        'Registrant ID':                    'registrant_id',
        'Recipient ID':                     'recipient_id',
        'Record ID':                        'record_id'
    }

    class Meta:
        db_table = 'fara_contribution'
        managed = False


class Disbursement(models.Model):
    import_reference = models.ForeignKey(Import)
    date = models.CharField(max_length=15)
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
    FIELD_MAP = {
        'Date':             'date',
        'Amount':           'amount',
        'Client':           'client',
        'Registrant':       'registrant',
        'Purpose':          'purpose',
        'To Subcontractor': 'to_subcontractor',
        'Source':           'source',
        'Document ID':      'document_id',
        'Registrant ID':    'registrant_id',
        'Client ID':        'client_id',
        'Location ID':      'location_id',
        'Subcontractor ID': 'subcontractor_id',
        'Record ID':        'record_id'
    }

    class Meta:
        db_table = 'fara_disbursement'
        managed = False


class Payment(models.Model):
    import_reference = models.ForeignKey(Import)
    date = models.CharField(max_length=15)
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
    FIELD_MAP = {
        'Date':                 'date',
        'Amount':               'amount',
        'Client':               'client',
        'Registrant':           'registrant',
        'Purpose':              'purpose',
        'From subcontractor':   'from_contractor',
        'Source':               'source',
        'Document ID':          'document_id',
        'Registrant ID':        'registrant_id',
        'Client ID':            'client_id',
        'Location ID':          'location_id',
        'Subcontractor ID':     'subcontractor_id',
        'Record ID':            'record_id'
    }

    class Meta:
        db_table = 'fara_payment'
        managed = False
