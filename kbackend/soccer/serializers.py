from rest_framework import serializers

from soccer.models import SoccerStat, Match


class SoccerStatCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SoccerStat
        fields = ('user', 'stat_type', 'value', 'stat_uuid', 'match', 'side')

    def get_or_create(self):
        self.is_valid(raise_exception=True)
        uuid = self.validated_data['stat_uuid']
        stat = SoccerStat.objects.filter(stat_uuid=uuid).first()
        if stat:
            # Already exists
            return stat, False

        return self.save(), True


class UsernamesField(serializers.ListField):
    username = serializers.CharField(max_length=63)


class MatchCreateSerializer(serializers.ModelSerializer):
    competition = serializers.CharField(source='competition_name', required=False)
    home_players = UsernamesField(allow_empty=False)
    away_players = UsernamesField(allow_empty=False)

    class Meta:
        model = Match
        fields = ('competition', 'home_team', 'away_team', 'home_players', 'away_players')

    def validate(self, data):
        home_players = data['home_players']
        away_players = data['away_players']
        users_in_both_teams = [user for user in home_players if user in away_players]
        if len(users_in_both_teams) > 0:
            raise serializers.ValidationError('Some players are present in both teams ({})'.format(', '.join(users_in_both_teams)))
        return data


class MatchSerializer(serializers.ModelSerializer):
    competition = serializers.CharField(source='competition_name', required=False)

    class Meta:
        model = Match
        fields = ('id', 'competition', 'home_team', 'away_team')
