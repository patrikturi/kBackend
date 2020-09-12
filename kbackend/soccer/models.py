from django.db import models
from django.conf import settings

SOCCER_STAT_TYPES = [
    ('goal', 'Goal'),
    ('assist', 'Assist'),
    ('yellow', 'Yellow Card'),
    ('red', 'Red Card'),
    ('sub off', 'Substitute Off'),
    ('sub on', 'Substitute On'),
    ('kcoins', 'kCoins'),
]

MATCH_SIDES = [
    ('home', 'Home'),
    ('away', 'Away'),
]


class Match(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    home_team = models.CharField(max_length=40)
    away_team = models.CharField(max_length=40)


class SoccerStat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    stat_type = models.CharField(max_length=10, choices=SOCCER_STAT_TYPES)
    value = models.IntegerField()
    stat_uuid = models.CharField(max_length=36)
    match = models.ForeignKey(Match, null=True, on_delete=models.SET_NULL)
    side = models.CharField(max_length=4, blank=True, choices=MATCH_SIDES)
