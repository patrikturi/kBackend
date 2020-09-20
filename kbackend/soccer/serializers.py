from rest_framework import serializers

from soccer.models import SoccerStat, Match


class SoccerStatCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SoccerStat
        fields = ('user', 'stat_type', 'value', 'stat_uuid', 'match', 'side')


class UsernamesField(serializers.ListField):
    username = serializers.CharField(max_length=63)


class MatchCreateSerializer(serializers.ModelSerializer):
    competition = serializers.Field(source='competition_name', required=False)
    home_players = UsernamesField()
    away_players = UsernamesField()

    class Meta:
        model = Match
        fields = ('competition', 'home_team', 'away_team', 'home_players', 'away_players')
