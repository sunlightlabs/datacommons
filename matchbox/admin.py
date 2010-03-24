from django.contrib import admin
from matchbox.models import Entity, EntityAlias, EntityAttribute, Normalization, MergeCandidate, EntityNote

class AliasInline(admin.TabularInline):
    model = EntityAlias

class AttributeInline(admin.TabularInline):
    model = EntityAttribute

class EntityAdmin(admin.ModelAdmin):
    inlines = [AliasInline, AttributeInline]
    list_filter = ('type',)

class MergeCandidateAdmin(admin.ModelAdmin):
    list_display = ('name','priority','owner','owner_timestamp')
    list_filter = ('priority',)

class EntityNodeAdmin(admin.ModelAdmin):
    raw_id_fields = ('entity',)

admin.site.register(Entity, EntityAdmin)
admin.site.register(Normalization)
admin.site.register(EntityNote, EntityNodeAdmin)
admin.site.register(MergeCandidate, MergeCandidateAdmin)