from dcdata.utils.sql import django2sql_names, is_disjoint, dict_union
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from common.db.fields.uuid import UUIDField
import datetime


class ExtensibleModel(models.Model):
    def to_dict(self):
        dict = model_to_dict(self)
        for p in self.extended_properties:
            obj = getattr(self, p)

            try:
                dict[p] = obj.public_representation()
            except AttributeError:
                dict[p] = obj

        return dict

    class Meta:
        abstract = True

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
    id = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=entity_types, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    reviewer = models.CharField(max_length=255, default="")

    def __unicode__(self):
        return self.name

    possible_sources = 'sunlight_info wikipedia_info bioguide_info'.split()

    def public_representation(self):
        return { 'name': self.name, 'id': self.id, 'type': self.type }

    def sourced_metadata_in_order(self):
        sources = []
        for attr in self.possible_sources:
            if hasattr(self, attr):
                sources.append((attr, getattr(self, attr)))

        return sources

    def _get_sourced_data_as_dict(self):
        sources_dict = [(name, model_to_dict(x)) for (name, x) in self.sourced_metadata_in_order()]
        sources_dict.reverse()
        compiled_dict = {}

        if len(sources_dict):
            for (source_name, source_dict) in sources_dict:
                source_dict['source_name'] = source_name
                compiled_dict.update(source_dict)

        return compiled_dict

    sourced_metadata = property(_get_sourced_data_as_dict)

    def _get_all_metadata_as_dict(self):
        # sourced metadata
        metadata = {}

        # our type-specific metadata
        if self.type == 'politician' and hasattr(self, 'politician_metadata'):
            metadata.update(model_to_dict(self.politician_metadata))
        elif self.type == 'organization' and hasattr(self, 'organization_metadata'):
            metadata.update(self.organization_metadata.to_dict())
        elif self.type == 'individual':
            # in the future, individuals should probably have their own metadata table,
            # just like the other entity types, but since it would essentially be a
            # dummy table and we only have one attribute (on its own table), leaving it out for now
            metadata.update({'affiliated_organizations': [ x.organization_entity.public_representation() for x in self.affiliated_organizations.all()]})

        metadata.update(self._get_sourced_data_as_dict())

        # don't show the primary key of the metadata object, as it is meaningless
        if metadata.has_key('id'):
            del metadata['id']

        return metadata

    metadata = property(_get_all_metadata_as_dict)

    class Meta:
        db_table = 'matchbox_entity'


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


    ENTITY_ID_NAMESPACE = 'urn:transparencydata:entity_id'

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


class OrganizationMetadata(ExtensibleModel):
    extended_properties = ['parent_entity', 'child_entities']
    # parent_entity needs to be called here so that it populates the whole object instead of just returning the entity_id

    entity = models.OneToOneField(Entity, related_name='organization_metadata', null=False, unique=True)

    lobbying_firm = models.BooleanField(default=False)
    parent_entity = models.ForeignKey(Entity, related_name='child_entity_set', null=True)
    industry_entity = models.ForeignKey(Entity, related_name='industry_entity', null=True)

    def _child_entities(self):
        return [ x.entity.public_representation() for x in self.entity.child_entity_set.all() ]

    child_entities = property(_child_entities)

    class Meta:
        db_table = 'matchbox_organizationmetadata'


class PoliticianMetadata(models.Model):
    entity = models.OneToOneField(Entity, related_name='politician_metadata', null=False)

    state = USStateField(blank=True, null=True)
    party = models.CharField(max_length=64, blank=True, null=True)
    seat  = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'matchbox_politicianmetadata'


class IndivOrgAffiliations(models.Model):
    individual_entity = models.ForeignKey(Entity, null=False, related_name="affiliated_organizations")
    organization_entity = models.ForeignKey(Entity, null=False, related_name="affiliated_individuals")

    class Meta:
        db_table = 'matchbox_indivorgaffiliations'


class BioguideInfo(models.Model):
    entity = models.OneToOneField(Entity, related_name='bioguide_info', null=False)

    bioguide_id      = models.CharField(max_length=7, blank=True, null=True)
    bio              = models.TextField(null=True)
    bio_url          = models.URLField(null=True)
    years_of_service = models.CharField(max_length=12, null=True)
    photo_url        = models.URLField(null=True)

    created_on       = models.DateField(auto_now_add=True)
    updated_on       = models.DateField(auto_now=True, null=True)

    class Meta:
        db_table = 'matchbox_bioguideinfo'

class WikipediaInfo(models.Model):
    entity = models.OneToOneField(Entity, related_name='wikipedia_info', null=False)

    bio        = models.TextField(null=True)
    bio_url    = models.URLField(null=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True, null=True)

    class Meta:
        db_table = 'matchbox_wikipediainfo'


class SunlightInfo(models.Model):
    entity = models.OneToOneField(Entity, related_name='sunlight_info', null=False)

    bio        = models.TextField(null=True)
    photo_url  = models.URLField(null=True)
    notes      = models.CharField(max_length=255, null=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True, null=True)

    class Meta:
        db_table = 'matchbox_sunlightinfo'

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
    entity = models.ForeignKey(Entity, related_name="merge_candidates", blank=True, null=True)
    priority = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name="merge_candidates", blank=True, null=True)
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

assert is_disjoint(_entity_names, _alias_names, _attribute_names, _normalization_names, _merge_names)
sql_names = dict_union(_entity_names, _alias_names, _attribute_names, _normalization_names, _merge_names)


