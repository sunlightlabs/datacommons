from django.conf import settings
from django.db import models
from dcdata.utils.sql import django2sql_names, is_disjoint, dict_union
from strings.normalizer import basic_normalizer
import datetime

#
# entity reference field
#

class EntityRefCache(dict):
    def register(self, model, field):
        if not model in self:
            self[model] = []
        self[model].append(field)
       
entityref_cache = EntityRefCache()

class EntityRef(models.ForeignKey):
   
    def __init__(self, related_name, ignore=False, *args, **kwargs):
        kwargs['related_name'] = related_name
        kwargs['blank'] = True
        kwargs['null'] = True
        super(EntityRef, self).__init__(Entity, *args, **kwargs)
        self._ignore = ignore
       
    def contribute_to_class(self, cls, name):
        super(EntityRef, self).contribute_to_class(cls, name)
        if not self._ignore:
            entityref_cache.register(cls, name)

#
# models
#

entity_types = [(s, s) for s in getattr(settings, 'ENTITY_TYPES', [])]

class Entity(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=entity_types, default=entity_types[0][0])
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    reviewer = models.CharField(max_length=255, default="")
    notes = models.TextField(default="", blank=True)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def save(self, **kwargs):
        super(Entity, self).save(**kwargs)
        try:
            Normalization.objects.get(original=self.name)
        except Normalization.DoesNotExist:
            Normalization(
                original=self.name,
                normalized=basic_normalizer(self.name)
            ).save()
    
    
class EntityAlias(models.Model):
    entity = EntityRef(related_name='aliases')
    alias = models.CharField(max_length=255)
    
    class Meta:
        ordering = ('alias',)
    
    def __unicode__(self):
        return self.alias


# should this be called 'external ID' or attribute?
class EntityAttribute(models.Model):
    entity = EntityRef(related_name='attributes')
    namespace = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    
    class Meta:
        ordering = ('namespace',)
    
    def __unicode__(self):
        return u"%s:%s" % (self.namespace, self.value)
    
    
class Normalization(models.Model):
    original = models.CharField(max_length=255, primary_key=True)
    normalized = models.CharField(max_length=255)
    
    class Meta:
        ordering = ('original',)
    
    def __unicode__(self):
        return self.original
    

_entity_names = django2sql_names(Entity)
_alias_names = django2sql_names(EntityAlias)
_attribute_names = django2sql_names(EntityAttribute)
_normalization_names = django2sql_names(Normalization)

assert is_disjoint(_entity_names, _alias_names, _attribute_names, _normalization_names)
sql_names = dict_union(_entity_names, _alias_names, _attribute_names, _normalization_names)
 
    
