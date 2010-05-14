from django.contrib import admin
from dcdata.grants.models import Grant

class GrantAdmin(admin.ModelAdmin):
    pass

admin.site.register(Grant, GrantAdmin)