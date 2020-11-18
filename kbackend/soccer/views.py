import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.basic_auth import ServerBasicAuthentication
from soccer.helpers import perform_create_stat, perform_create_match

logger = logging.getLogger('soccer')


class SoccerStatsView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        created = perform_create_stat(request.data)

        logger.info({'event': 'create_stat', 'data': request.data})

        ret_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({}, status=ret_status)


class MatchesView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        match = perform_create_match(request.data)

        logger.info({'event': 'create_match', 'data': request.data})

        return Response({'id': match.id}, status=status.HTTP_201_CREATED)
