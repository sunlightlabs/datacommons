from django.contrib import admin
from dcdata.contribution.models import Contribution

class ContributionAdmin(admin.ModelAdmin):
    list_display = ('date','contributor_name','contributor_city','contributor_state','amount','recipient_type','recipient_name','organization_name','committee_name','seat','seat_status')
    #list_filter = ('recipient_type','seat')

admin.site.register(Contribution, ContributionAdmin)