from django.contrib import admin
from dcentity.models import Entity, EntityAlias, EntityAttribute, Normalization, MergeCandidate, WikipediaInfo, BioguideInfo, SunlightInfo

class AliasInline(admin.TabularInline):
    model = EntityAlias

class AttributeInline(admin.TabularInline):
    model = EntityAttribute
    
class WikipediaInline(admin.TabularInline):
    model = WikipediaInfo
    
class BioguideInline(admin.TabularInline):
    model = BioguideInfo

class SunlightInline(admin.TabularInline):
    model = SunlightInfo

class EntityAdmin(admin.ModelAdmin):
    inlines = [AliasInline, AttributeInline, WikipediaInline, BioguideInline, SunlightInline]
    list_filter = ('type',)
    search_fields = ['name','aliases__alias','id']

class MergeCandidateAdmin(admin.ModelAdmin):
    list_display = ('name','priority','owner','owner_timestamp')
    list_filter = ('priority',)

admin.site.register(Entity, EntityAdmin)
admin.site.register(Normalization)
admin.site.register(MergeCandidate, MergeCandidateAdmin)