from django.contrib import admin
from dcentity.models import Entity, EntityAlias, EntityAttribute, Normalization, MergeCandidate, WikipediaInfo, BioguideInfo, SunlightInfo, VotesmartInfo, IndustryMetadata, PoliticianMetadata, OrganizationMetadata

class AliasInline(admin.TabularInline):
    model = EntityAlias

class AttributeInline(admin.TabularInline):
    model = EntityAttribute
    
class WikipediaInline(admin.TabularInline):
    model = WikipediaInfo
    readonly_fields = [x.name for x in  model._meta.fields]
    
class BioguideInline(admin.TabularInline):
    model = BioguideInfo
    readonly_fields = [x.name for x in model._meta.fields]

class SunlightInline(admin.TabularInline):
    model = SunlightInfo
    
class VotesmartInline(admin.TabularInline):
    model = VotesmartInfo
    readonly_fields = [x.name for x in model._meta.fields]

class IndustryMetadataInline(admin.TabularInline):
    model = IndustryMetadata
    fk_name = "entity"

class OrganizationMetadataInline(admin.TabularInline):
    model = OrganizationMetadata
    fk_name = "entity"

class EntityAdmin(admin.ModelAdmin):
    inlines = [AliasInline, AttributeInline, WikipediaInline, BioguideInline, SunlightInline, VotesmartInline]
    #PoliticianMetadataInline, IndustryMetadataInline, OrganizationMetadataInline
    list_filter = ('type',)
    search_fields = ['aliases__alias']
    readonly_fields = ['timestamp','should_delete']
    """
    def queryset(self, request):
            qs = super(MyModelAdmin, self).queryset(request)
            if request.type = 'politi':
                return qs
            return qs.filter(author=request.user)
    """

class MergeCandidateAdmin(admin.ModelAdmin):
    list_display = ('name','priority','owner','owner_timestamp')
    list_filter = ('priority',)

admin.site.register(Entity, EntityAdmin)
admin.site.register(Normalization)
admin.site.register(MergeCandidate, MergeCandidateAdmin)