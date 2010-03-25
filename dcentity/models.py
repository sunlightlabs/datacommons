
from uuid import uuid4
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Sum
from dcdata.utils.sql import django2sql_names, is_disjoint, dict_union
from dcdata.utils.strings.normalizer import basic_normalizer
import datetime

#
# entity reference field
#

class EntityRefCache(dict):
    def register(self, model, field):
        if not model in self:
            self[model] = []
        self[model].append(field)
    def for_model_name(self, name):
        name = name.lower()
        for key, value in self.iteritems():
            if key._meta.object_name.lower() == name:
                return (key, self[key])
       
entityref_cache = EntityRefCache()

class EntityRef(models.CharField):
   
    def __init__(self, related_name, ignore=False, *args, **kwargs):
        kwargs['max_length'] = 32
        kwargs['blank'] = True
        kwargs['null'] = True
        kwargs['db_index'] = True
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
    
    def with_id(self, entity_id):
        return Entity.objects.filter(
            Q(id=entity_id) | Q(attributes__namespace=EntityAttribute.ENTITY_ID_NAMESPACE, attributes__value=entity_id))
    
    def with_attribute(self, namespace, value=None):
        qs = Entity.objects.filter(attributes__namespace=namespace)
        if value:
            qs = qs.filter(attributes__value=value)
        return qs
        
    # is this used?
    def merge(self, name, type_, entity_ids):
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
    contribution_count = models.IntegerField(null=True, blank=True)
    contribution_total_given = models.DecimalField(null=True, blank=True, default=0, max_digits=15, decimal_places=2)    
    contribution_total_received = models.DecimalField(null=True, blank=True, default=0, max_digits=15, decimal_places=2)    

    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = 'matchbox_entity'
    

class EntityNote(models.Model):
    entity = models.ForeignKey(Entity, related_name='notes')
    user = models.ForeignKey(User, related_name="entity_notes")
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    
    class Meta:
        ordering = ('-timestamp',)
        db_table = 'matchbox_entitynote'
    
    def __unicode__(self):
        return self.content
    
    
    
class EntityAlias(models.Model):
    entity = models.ForeignKey(Entity, related_name='aliases', null=False)
    alias = models.CharField(max_length=255, null=False)
    verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('alias',)
        db_table = 'matchbox_entityalias'
    
    def __unicode__(self):
        return self.alias


# should this be called 'external ID' or attribute?
class EntityAttribute(models.Model):
    entity = models.ForeignKey(Entity, related_name='attributes', null=False)
    namespace = models.CharField(max_length=255, null=False)
    value = models.CharField(max_length=255, null=False)
    verified = models.BooleanField(default=False)
    
    
    ENTITY_ID_NAMESPACE = 'urn:matchbox:entity_id'
    
    class Meta:
        ordering = ('namespace',)
        db_table = 'matchbox_entityattribute'
    
    def __unicode__(self):
        return u"%s:%s" % (self.namespace, self.value)
    
    
class Normalization(models.Model):
    original = models.CharField(max_length=255, primary_key=True)
    normalized = models.CharField(max_length=255)
    
    class Meta:
        ordering = ('original',)
        db_table = 'matchbox_normalization'
    
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
        db_table = 'matchbox_mergecandidate'
    
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
_merge_names = django2sql_names(MergeCandidate)
_note_names = django2sql_names(EntityNote)

assert is_disjoint(_entity_names, _alias_names, _attribute_names, _note_names, _normalization_names, _merge_names)
sql_names = dict_union(_entity_names, _alias_names, _attribute_names, _note_names, _normalization_names, _merge_names)
 
    
