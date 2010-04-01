from django.contrib import admin
from dcdata.lobbying.models import Lobbyist, Lobbying, Agency

class LobbyistAdmin(admin.ModelAdmin):
    list_display = ('lobbyist_name','year','government_position','member_of_congress')
    list_filter = ('year','member_of_congress')
    search_fields = ('lobbyist_name',)

# class LobbyistInline(admin.StackedInline):
#     model = Lobbyist

class LobbyingAdmin(admin.ModelAdmin):    
    search_fields = ('registrant_name','client_name')
    list_display = ('transaction_id', 'year','registrant_name','amount','client_name','client_parent_name')
    list_filter = ('year',)
    #inlines = (LobbyistInline,)

admin.site.register(Lobbyist, LobbyistAdmin)
admin.site.register(Lobbying, LobbyingAdmin)
admin.site.register(Agency)