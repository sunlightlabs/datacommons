

from django.db import models
from datetime import datetime

from sql_utils import django2sql_names, is_disjoint, dict_union


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


entity_types = (('organization', 'organization'),('individual','individual'),('PAC','PAC'),('candidate', 'candidate'),('other','other'))

class Entity(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=entity_types, default=entity_types[0][0])
    timestamp = models.DateTimeField(default=datetime.now)
    reviewer = models.CharField(max_length=255, default="")
    notes = models.TextField(default="")
    
    
class EntityAlias(models.Model):
    entity = EntityRef(related_name='aliases', primary_key=True)
    alias = models.CharField(max_length=255)


# should this be called 'external ID' or attribute?
class EntityAttribute(models.Model):
    entity = EntityRef(related_name='attributes', primary_key=True)
    namespace = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    
    
class Normalization(models.Model):
    original = models.CharField(max_length=255, primary_key=True)
    normalized = models.CharField(max_length=255)
    
    

_entity_names = django2sql_names(Entity)
_alias_names = django2sql_names(EntityAlias)
_attribute_names = django2sql_names(EntityAttribute)
_normalization_names = django2sql_names(Normalization)

assert is_disjoint(_entity_names, _alias_names, _attribute_names, _normalization_names)
sql_names = dict_union(_entity_names, _alias_names, _attribute_names, _normalization_names)
 
    
