from django.contrib import admin
from Fifa.models import League, Player, Match, PositionTable, RegistrationLeague, Team

admin.site.register(League)

admin.site.register(Match)
admin.site.register(PositionTable)
admin.site.register(Player)
admin.site.register(RegistrationLeague)
admin.site.register(Team)
