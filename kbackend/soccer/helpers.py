import logging

from rest_framework.response import Response
from rest_framework import status

from soccer.serializers import SoccerStatCreateSerializer
from soccer.models import SoccerStat
from users.models import User

logger = logging.getLogger('soccer')


def perform_create_stat(data):
    username = data.get('username')

    create_data = dict(data)
    create_data.pop('username', None)
    stat, created = create_stat(username, create_data)

    if not stat:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ret_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK

    logger.info({'event': 'create_stat', 'created': created, **create_data})

    return Response({}, status=ret_status)


def create_stat(username, data):

    if not username:
        return None, False

    user = User.get_or_create(username)
    data['user'] = user.id

    serializer = SoccerStatCreateSerializer(data=data)
    if not serializer.is_valid():
        return None, False

    stat_uuid = data['stat_uuid']
    stat_type = data['stat_type']
    value = data['value']

    stat = SoccerStat.objects.filter(stat_uuid=stat_uuid).first()
    if stat:
        # Already exists
        return stat, False

    stat = serializer.save()
    user.add_stat(stat_type, value)
    return stat, True
