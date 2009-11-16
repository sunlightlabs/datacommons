from django.contrib import admin
from matchbox.models import Entity, EntityAlias, EntityAttribute, Normalization, MergeCandidate

class AliasInline(admin.TabularInline):
    model = EntityAlias

class AttributeInline(admin.TabularInline):
    model = EntityAttribute

class EntityAdmin(admin.ModelAdmin):
    inlines = [AliasInline, AttributeInline]

class MergeCandidateAdmin(admin.ModelAdmin):
    list_display = ('name','priority','owner','owner_timestamp')
    list_filter = ('priority',)

admin.site.register(Entity, EntityAdmin)
admin.site.register(Normalization)
admin.site.register(MergeCandidate, MergeCandidateAdmin)