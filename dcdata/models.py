from django.db import models
from matchbox.models import entityref_cache
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

class DataCommonsModelManager(models.Manager):
    def with_entity(self, entity, fields=None):
        if not fields:
            fields = entityref_cache.get(self.model, None)
        if fields:
            q = reduce(lambda x, y: x | y, (Q(**{field: entity.pk}) for field in fields))
            return self.model.objects.filter(q)

class DataCommonsModel(models.Model):
    objects = DataCommonsModelManager()
    import_reference = models.ForeignKey(Import)
    
    class Meta:
        abstract = True