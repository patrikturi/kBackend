from rest_framework.views import APIView

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from soccer.helpers import perform_create_stat

class SoccerStats(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        return perform_create_stat(request.data)
