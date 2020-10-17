import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from core.settings.common import *  # noqa: F401, F403
from core.settings.common import BASE_DIR, MIDDLEWARE


if not os.environ.get('LOCAL_TEST'):
    sentry_sdk.init(
        dsn="https://918cdbc4393a4dc0aa38530f61da9daf@o448987.ingest.sentry.io/5431213",
        integrations=[DjangoIntegration()],

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

os.makedirs(BASE_DIR / 'core' / 'logs' / 'gunicorn_access', exist_ok=True)
os.makedirs(BASE_DIR / 'core' / 'logs' / 'gunicorn_error', exist_ok=True)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
# TODO: SECURE_HSTS_SECONDS

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

WSGI_APPLICATION = 'core.wsgi.application'

MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# TODO: use posgres

# TODO
BASIC_TOKENS = [
    '***REMOVED***',
    '***REMOVED***'
]

CORS_ALLOWED_ORIGINS = ['https://ksoccersl.com', 'https://kfrontend-staging.firebaseapp.com']

CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ['ksoccersl.com', 'kfrontend-staging.firebaseapp.com']
