from django.contrib import admin
from dcdata.contracts.models import Contract

class ContractAdmin(admin.ModelAdmin):
    pass

admin.site.register(Contract, ContractAdmin)