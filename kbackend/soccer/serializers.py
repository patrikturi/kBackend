from rest_framework import serializers

from soccer.models import SoccerStat


class SoccerStatCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SoccerStat
        fields = ('user', 'stat_type', 'value', 'stat_uuid', 'match', 'side')
