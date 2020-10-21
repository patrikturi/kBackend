from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator


class CsrfView(APIView):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"token": request.META['CSRF_COOKIE']})
