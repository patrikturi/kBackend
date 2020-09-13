from django.contrib import admin
from soccer.models import Match, MatchParticipation, SoccerStat


class MatchAdmin(admin.ModelAdmin):
    pass


class MatchParticipationAdmin(admin.ModelAdmin):
    pass


class SoccerStatAdmin(admin.ModelAdmin):
    pass


admin.site.register(Match, MatchAdmin)
admin.site.register(MatchParticipation, MatchParticipationAdmin)
admin.site.register(SoccerStat, SoccerStatAdmin)
