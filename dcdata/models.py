from django.db import models
from django.db.models import Q

class Import(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=255)
    description = models.TextField()
    imported_by = models.CharField(max_length=255)
    
    class Meta:
        ordering = ('-timestamp',)
    
    def __unicode__(self):
        return self.timestamp.isoformat()

class DataCommonsModel(models.Model):
    import_reference = models.ForeignKey(Import)
    
    class Meta:
        abstract = True