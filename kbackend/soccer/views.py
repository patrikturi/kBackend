import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from soccer.helpers import perform_create_stat, perform_create_match

logger = logging.getLogger('soccer')


class SoccerStatsView(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        created = perform_create_stat(request.data)

        logger.info({'event': 'create_stat', 'data': request.data})

        ret_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({}, status=ret_status)


class MatchesView(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        match = perform_create_match(request.data)

        logger.info({'event': 'create_match', 'data': request.data})

        return Response({'id': match.id}, status=status.HTTP_201_CREATED)
