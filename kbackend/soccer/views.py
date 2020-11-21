import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.basic_auth import ServerBasicAuthentication
from soccer.helpers import perform_create_match
from users.models import User
from soccer.serializers import SoccerStatCreateSerializer

logger = logging.getLogger('soccer')


class SoccerStatsView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.create_stat(request.user, request.data)

    @classmethod
    def create_stat(cls, basic_user, data):
        create_data = dict(data)
        username = create_data.pop('username', None)

        user = User.get_or_create(username)
        data['user'] = user.id

        serializer = SoccerStatCreateSerializer(data=data)
        stat, created = serializer.get_or_create()

        if created:
            user.add_stat(data['stat_type'], data['value'])

        logger.info({'event': 'create_stat', 'created': created, 'data': create_data, 'basic_user': basic_user.username})

        ret_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({}, status=ret_status)


class MatchesView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        match = perform_create_match(request.data)

        logger.info({'event': 'create_match', 'data': request.data})

        return Response({'id': match.id}, status=status.HTTP_201_CREATED)
