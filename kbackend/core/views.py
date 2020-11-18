from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.basic_auth import ServerBasicAuthentication


class CsrfView(APIView):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"csrftoken": request.META['CSRF_COOKIE']})


class BasicAuthTestView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response()
