from ratelimit.core import is_ratelimited
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import status

from core.helpers import log_ratelimit


ratelimit_config = {'key': 'ip', 'rate': '10/30m'}


def login_wrapper(login_func):

    def admin_login(request, **kwargs):
        ratelimit_config['fn'] = login_wrapper

        if is_ratelimited(request, **ratelimit_config, increment=False):
            username = request.POST.get('username')
            log_ratelimit(request, username=username)
            return HttpResponse('Too many failed login attemps. Please try again later.', status=status.HTTP_429_TOO_MANY_REQUESTS)

        response = login_func(request, **kwargs)
        if isinstance(response, HttpResponseRedirect):
            return response

        form = response.context_data['form']

        if form.is_bound and not form.is_valid():
            is_ratelimited(request, **ratelimit_config, increment=True)

        return response

    return admin_login
