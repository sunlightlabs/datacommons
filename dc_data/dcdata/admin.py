from django.contrib import admin
from dcdata.models import Import

class ImportAdmin(admin.ModelAdmin):
    list_display = ('timestamp','source','description','imported_by')
    list_filter = ('source',)

admin.site.register(Import, ImportAdmin)