from django.db import models


COMPETITION_TYPES = [
    ('league', 'League'), 
    ('tournament', 'Tournament'),
    ('championship', 'Championship')
]

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Competition(BaseModel):
    competition_type = models.CharField(max_length=16,
                                        choices=COMPETITION_TYPES,
                                        help_text=
"""
League has a standings table and results in a ranking
Tournament has a bracket and results in a single champion
Championship starts as a League and ends with a tournament of the top teams
""")
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Team(BaseModel):
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=256)
    competitions = models.ManyToManyField(Competition)
    is_active = models.BooleanField(default=True)


# Adding "Soccer" to the name because searching for "Field" would return a lot of results
class SoccerField(BaseModel):
    name = models.CharField(max_length=40, unique=True)
    # Let's not mess with uploading files for now
    photo_url = models.URLField(help_text='Admins can upload files to the kSoccer dropbox account and link them')
    sl_url = models.URLField(blank=True, help_text='Remove this field if the field no longer exists')


MATCH_STAT_TYPES = [
    ('goal', 'Goal'),
    ('yellow', 'Yellow Card'),
    ('red', 'Red Card'),
    ('sub off', 'Substitute Off'),
    ('sub on', 'Substitute On'),
]


class Match(BaseModel):
    start_date = models.DateTimeField()
    home_team = models.ForeignKey(Team, null=True, related_name='home_team',
                                  on_delete=models.PROTECT, help_text=
                                  'Can be null for a scheduled match in a tournament (opponent is TBD)')
    away_team = models.ForeignKey(Team, null=True, related_name='away_team',
                                  on_delete=models.PROTECT)
    soccer_field = models.ForeignKey(SoccerField, null=True, on_delete=models.PROTECT)


class LeaderboardPlayer(BaseModel):
    # http://wiki.secondlife.com/wiki/Category:LSL_Avatar/Name
    # http://wiki.secondlife.com/wiki/Limits
    sl_username = models.CharField(max_length=63, unique=True, help_text=
        'Format: "firstname.lastname", all lower case, modern accounts have only firstname\n \
         Should be possible to connect to a registered player - later when we do have registration.')
    display_name = models.CharField(max_length=31, blank=True)


class MatchStat(BaseModel):
    stat_type = models.CharField(max_length=16, choices=MATCH_STAT_TYPES)
    time = models.TimeField(null=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, help_text=
        'Storing both team and player because the player can switch teams and also makes queries easier')
    player = models.ForeignKey(LeaderboardPlayer, null=True, on_delete=models.SET_NULL)
