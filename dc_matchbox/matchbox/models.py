
from uuid import uuid4
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Sum
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

# class EntityRef(models.ForeignKey):
#    
#     def __init__(self, related_name, ignore=False, *args, **kwargs):
#         kwargs['related_name'] = related_name
#         kwargs['blank'] = True
#         kwargs['null'] = True
#         super(EntityRef, self).__init__(Entity, *args, **kwargs)
#         self._ignore = ignore
#        
#     def contribute_to_class(self, cls, name):
#         super(EntityRef, self).contribute_to_class(cls, name)
#         if not self._ignore:
#             entityref_cache.register(cls, name)

class EntityRef(models.CharField):
   
    def __init__(self, related_name, ignore=False, *args, **kwargs):
        kwargs['max_length'] = 32
        kwargs['blank'] = True
        kwargs['null'] = True
        super(EntityRef, self).__init__(*args, **kwargs)
        self._ignore = ignore
        self._label = related_name
       
    def contribute_to_class(self, cls, name):
        super(EntityRef, self).contribute_to_class(cls, name)
        if not self._ignore:
            entityref_cache.register(cls, name)
    
    def entity(self):
        pass

#
# models
#

entity_types = [(s, s) for s in getattr(settings, 'ENTITY_TYPES', [])]

class EntityManager(models.Manager):
    def merge(self, name, type_, entity_ids):
        #count = Entity.objects.filter(pk__in=entity_ids).aggregate(Sum('count'))
        #entity = Entity(name=name, type=type_, count=count)
        new_entity = Entity(name=name, type=type_)
        for entity_id in entity_ids:
            old_entity = Entity.objects.get(pk=entity_id)
            for model, fields in entityref_cache.iteritems():
                for field in fields:
                    model.objects.filter(**{field: old_entity}).update(**{field: new_entity})

class Entity(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=lambda: uuid4().hex)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=entity_types, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    reviewer = models.CharField(max_length=255, default="")
    notes = models.TextField(default="", blank=True)
    count = models.IntegerField(default=0)
    
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
    entity = models.ForeignKey(Entity, related_name='aliases', null=False)
    alias = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ('alias',)
    
    def __unicode__(self):
        return self.alias


# should this be called 'external ID' or attribute?
class EntityAttribute(models.Model):
    entity = models.ForeignKey(Entity, related_name='attributes', null=False)
    namespace = models.CharField(max_length=255, null=False)
    value = models.CharField(max_length=255, null=False)
    
    ENTITY_ID_NAMESPACE = 'urn:matchbox:entity_id'
    
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

#
# merge candidate
#

class MergeCandidateManager(models.Manager):
    def pending(self, user, limit=20):
        ago15min = datetime.datetime.utcnow() - datetime.timedelta(0, 0, 0, 0, 15)
        return MergeCandidate.objects.filter(Q(owner_timestamp__isnull=True) | Q(owner_timestamp__lte=ago15min) | Q(owner=user))[:limit]

class MergeCandidate(models.Model):
    
    objects = MergeCandidateManager()
    
    name = models.CharField(max_length=255)
    entity = models.ForeignKey(Entity, blank=True, null=True)
    priority = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, blank=True, null=True)
    owner_timestamp = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ('-priority','timestamp')
    
    def __unicode__(self):
        return self.name
    
    def lock(self, user):
        self.owner = user 
        self.owner_timestamp = datetime.datetime.utcnow()
        self.save()
    
    def is_locked(self):
        ago15min = datetime.datetime.utcnow() - datetime.timedelta(0, 0, 0, 0, 15)
        return self.owner is not None and self.owner_timestamp >= ago15min
    

_entity_names = django2sql_names(Entity)
_alias_names = django2sql_names(EntityAlias)
_attribute_names = django2sql_names(EntityAttribute)
_normalization_names = django2sql_names(Normalization)

assert is_disjoint(_entity_names, _alias_names, _attribute_names, _normalization_names)
sql_names = dict_union(_entity_names, _alias_names, _attribute_names, _normalization_names)
 
    
