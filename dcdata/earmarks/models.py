from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import Import

to_do = (('there will', 'be choices'))

class Earmark(models.Model):
    import_reference = models.ForeignKey(Import)
    
    fiscal_year = models.IntegerField()
    
    budget_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    house_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    senate_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    final_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    
    # should we call it 'location' instead?
    city = models.CharField(max_length=128, blank=True)
    state = USStateField(blank=True)
    
    bill = model.CharField(max_length=64, choices=to_do, blank=False)
    bill_section = model.CharField(max_length=255, blank=True)
    bill_subsection = model.CharField(max_length=255, blank=True)
    
    # possible that we'll need to increase the length if we see long values
    description = model.CharField(max_length=255, blank=True)
    notes = model.CharField(max_length=255, blank=True)
    
    presidential = model.CharField(max_length=1, choices=to_do, blank=True)
    undisclosed = model.CharField(max_length=1, choices=to_do, blank=True)
    
    raw_recipient = model.CharField(max_length=128, blank=True)
    standardized_recipient = model.CharField(max_length=128, blank=True)


class Member(models.Model):
    earmark = models.ForeignKey(Earmark)
    
    chamber = model.CharField(max_length=1, choices=to_do)
    
    raw_name = model.CharField(max_length=64)
    raw_party = model.CharField(max_length=1, choices=to_do)
    raw_state = USStateField(blank=True)
    
    crp_id = models.CharField(max_length=128, blank=True)
    standardized_name = models.CharField(max_length=128, blank=True)
