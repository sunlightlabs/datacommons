from django.contrib import admin
from matchbox.models import Entity, EntityAlias, EntityAttribute

class AliasInline(admin.TabularInline):
    model = EntityAlias

class AttributeInline(admin.TabularInline):
    model = EntityAttribute

class EntityAdmin(admin.ModelAdmin):
    inlines = [AliasInline, AttributeInline]

admin.site.register(Entity, EntityAdmin)