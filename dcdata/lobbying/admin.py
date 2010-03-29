from django.contrib import admin
from dcdata.lobbying.models import Lobbyist, Lobbying, Agency

admin.site.register(Lobbyist)
admin.site.register(Lobbying)
admin.site.register(Agency)