from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from common.db.fields.uuid_field import UUIDField
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
# models
#

entity_types = [(s, s) for s in getattr(settings, 'ENTITY_TYPES', [])]


class Entity(models.Model):
    id = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=entity_types, blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)
    reviewer = models.CharField(max_length=255, default="")
    should_delete = models.BooleanField(default=False, null=False)
    flagged_on = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.name

    possible_sources = 'sunlight_info wikipedia_info bioguide_info'.split()

    def public_representation(self):
        """
            Returns a dict of the attributes we want to show in API results
        """
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
                [ source_dict.pop(x) for x in source_dict.keys() if source_dict[x] == None ]

                # this is displayed below the bio, so we'll only set it based on that field
                if source_dict.has_key('bio'):
                    source_dict['source_name'] = source_name

                compiled_dict.update(source_dict)

        return compiled_dict

    sourced_metadata = property(_get_sourced_data_as_dict)

    def _get_all_metadata_as_dict(self):
        # sourced metadata
        metadata = {}

        # our type-specific metadata
        if self.type == 'politician' and hasattr(self, 'politician_metadata_by_cycle'):
            for data_by_cycle in self.politician_metadata_by_cycle.all():
                metadata[data_by_cycle.cycle] = model_to_dict(data_by_cycle)
                del(metadata[data_by_cycle.cycle]['cycle'])
                del(metadata[data_by_cycle.cycle]['id'])
                del(metadata[data_by_cycle.cycle]['entity'])

            # assign latest cycle to old fields for backwards compatibility
            # (might not need this going forward)
            if hasattr(self, 'politician_metadata_for_latest_cycle'):
                latest = model_to_dict(self.politician_metadata_for_latest_cycle)
                del(latest['cycle'])
                del(latest['entity'])
                metadata.update(latest)
            else:
                metadata['seat'] = ''
                metadata['party'] = ''
                metadata['state'] = ''

            if hasattr(self, 'lobbying_activity'):
                metadata['revolving_door_entity'] = self.lobbying_activity.lobbyist_entity.public_representation()

        elif self.type == 'organization' and hasattr(self, 'organization_metadata_for_latest_cycle'):
            metadata.update(self.organization_metadata_for_latest_cycle.to_dict())

        elif self.type == 'individual':
            # in the future, individuals should probably have their own metadata table,
            # just like the other entity types, but since it would essentially be a
            # dummy table and we only have one attribute (on its own table), leaving it out for now
            metadata.update({'affiliated_organizations': [ x.organization_entity.public_representation() for x in self.affiliated_organizations.all()]})
            if hasattr(self, 'political_activity'):
                metadata['revolving_door_entity'] = self.political_activity.politician_entity.public_representation()

        elif self.type == 'industry' and hasattr(self, 'industry_metadata'):
            metadata.update(self.industry_metadata.to_dict())

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
    namespace = models.CharField(max_length=255, null=False)
    alias = models.CharField(max_length=255, null=False)

    class Meta:
        ordering = ('alias',)
        db_table = 'matchbox_entityalias'

    def __unicode__(self):
        return self.alias


class EntityNameParts(models.Model):
    alias  = models.OneToOneField(EntityAlias, related_name='name_parts', null=False)
    prefix = models.CharField(max_length=3, null=True)
    first  = models.CharField(max_length=32, null=True)
    middle = models.CharField(max_length=32, null=True)
    last   = models.CharField(max_length=32, null=True)
    suffix = models.CharField(max_length=3, null=True)

    class Meta:
        db_table = 'matchbox_entitynameparts'


# should this be called 'external ID' or attribute?
class EntityAttribute(models.Model):
    entity = models.ForeignKey(Entity, related_name='attributes', null=False)
    namespace = models.CharField(max_length=255, null=False)
    value = models.CharField(max_length=255, null=False)

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

    entity = models.OneToOneField(Entity, related_name='organization_metadata_by_cycle', null=False)

    cycle = models.PositiveSmallIntegerField()

    lobbying_firm   = models.BooleanField(default=False)
    parent_entity   = models.ForeignKey(Entity, related_name='child_entity_set_for_cycle', null=True)
    industry_entity = models.ForeignKey(Entity, related_name='industry_entity_for_cycle', null=True)

    def _child_entities(self):
        return [ x.entity.public_representation() for x in self.entity.child_entity_set.all() ]

    child_entities = property(_child_entities)

    class Meta:
        db_table = 'matchbox_organizationmetadata'


class OrganizationMetadataLatest(ExtensibleModel):
    extended_properties = ['parent_entity', 'child_entities']
    # parent_entity needs to be called here so that it populates the whole object instead of just returning the entity_id

    entity = models.OneToOneField(Entity, related_name='organization_metadata_for_latest_cycle', null=False, primary_key=True)

    lobbying_firm   = models.BooleanField(default=False)
    parent_entity   = models.ForeignKey(Entity, related_name='child_entity_set', null=True)
    industry_entity = models.ForeignKey(Entity, related_name='industry_entity', null=True)

    def _child_entities(self):
        return [ x.entity.public_representation() for x in self.entity.child_entity_set.all() ]

    child_entities = property(_child_entities)

    class Meta:
        db_table = 'organization_metadata_latest_cycle_view'
        managed = False


class PoliticianMetadata(models.Model):
    entity = models.ForeignKey(Entity, related_name='politician_metadata_by_cycle', null=False, db_index=True)

    cycle = models.PositiveSmallIntegerField()

    state         = USStateField(blank=True, null=True)
    state_held    = USStateField(blank=True, null=True)
    district      = models.CharField(max_length=8, blank=True, null=True)
    district_held = models.CharField(max_length=8, blank=True, null=True)
    party         = models.CharField(max_length=64, blank=True, null=True)
    seat          = models.CharField(max_length=64, blank=True, null=True)
    seat_held     = models.CharField(max_length=64, blank=True, null=True)
    seat_status   = models.CharField(max_length=10, blank=True, choices=(('incumbent', 'Incumbent'), ('challenger', 'Challenger'), ('open', 'Open')))
    seat_result   = models.CharField(max_length=4, blank=True, choices=(('win', 'Win'), ('loss', 'Loss')))

    class Meta:
        db_table = 'matchbox_politicianmetadata'

class PoliticianMetadataLatest(models.Model):
    entity = models.OneToOneField(Entity, related_name='politician_metadata_for_latest_cycle', null=False, primary_key=True)

    cycle = models.PositiveSmallIntegerField()

    state         = USStateField(blank=True, null=True)
    state_held    = USStateField(blank=True, null=True)
    district      = models.CharField(max_length=8, blank=True, null=True)
    district_held = models.CharField(max_length=8, blank=True, null=True)
    party         = models.CharField(max_length=64, blank=True, null=True)
    seat          = models.CharField(max_length=64, blank=True, null=True)
    seat_held     = models.CharField(max_length=64, blank=True, null=True)
    seat_status   = models.CharField(max_length=10, blank=True, choices=(('incumbent', 'Incumbent'), ('challenger', 'Challenger'), ('open', 'Open')))
    seat_result   = models.CharField(max_length=4, blank=True, choices=(('win', 'Win'), ('loss', 'Loss')))

    class Meta:
        db_table = 'politician_metadata_latest_cycle_view'
        managed = False

class IndustryMetadata(ExtensibleModel):
    entity = models.OneToOneField(Entity, related_name='industry_metadata', null=False)
    should_show_entity = models.BooleanField(default=True)
    parent_industry = models.ForeignKey(Entity, related_name='child_industry_set', null=True)

    extended_properties = ['parent_industry', 'child_industries']

    def _child_industries(self):
        return [x.entity.public_representation() for x in self.entity.child_industry_set.all()]

    child_industries = property(_child_industries)

    class Meta:
        db_table = 'matchbox_industrymetadata'

class IndivOrgAffiliations(models.Model):
    individual_entity = models.ForeignKey(Entity, null=False, related_name="affiliated_organizations")
    organization_entity = models.ForeignKey(Entity, null=False, related_name="affiliated_individuals")

    class Meta:
        db_table = 'matchbox_indivorgaffiliations'


class RevolvingDoor(models.Model):
    politician_entity = models.OneToOneField(Entity, null=False, related_name='lobbying_activity')
    lobbyist_entity = models.OneToOneField(Entity, null=False, related_name='political_activity')

    class Meta:
        db_table = 'matchbox_revolvingdoor'


class VotesmartInfo(models.Model):
    entity = models.OneToOneField(Entity, related_name='votesmart_info', null=False)

    votesmart_id = models.IntegerField()
    photo_url = models.URLField(null=True)

    class Meta:
        db_table = 'matchbox_votesmartinfo'

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
    photo_url  = models.URLField(null=True)

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


class PoliticianRelative(models.Model):
    entity = models.ForeignKey(Entity, related_name='relatives', null=False)

    raw_name = models.CharField(max_length=150, null=False)

    first_name  = models.CharField(max_length=50, null=True)
    middle_name = models.CharField(max_length=50, null=True)
    last_name   = models.CharField(max_length=50, null=True)

    relation = models.CharField(max_length=20, null=False, choices=[('child', 'Child'), ('partner', 'Partner')])

    class Meta:
        db_table = 'matchbox_politicianrelative'

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


