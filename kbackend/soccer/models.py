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

    competition_name = models.CharField(max_length=40, blank=True)

    home_team = models.CharField(max_length=40)
    away_team = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural = 'Matches'


class ParticipationManager(models.Manager):

    def bulk_create_team(self, match, users, side):
        participartions = [MatchParticipation(user=user, match=match, side=side) for user in users]
        self.bulk_create(participartions)


class MatchParticipation(models.Model):
    objects = ParticipationManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    match = models.ForeignKey(Match, null=True, on_delete=models.CASCADE)
    side = models.CharField(max_length=4, blank=True, choices=MATCH_SIDES)


class SoccerStat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    stat_uuid = models.CharField(max_length=36, db_index=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    stat_type = models.CharField(max_length=10, choices=SOCCER_STAT_TYPES)
    value = models.IntegerField()
    match = models.ForeignKey(Match, null=True, on_delete=models.CASCADE)
    side = models.CharField(max_length=4, blank=True, choices=MATCH_SIDES)
