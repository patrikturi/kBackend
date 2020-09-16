import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from core.settings.common import *
from core.settings.common import BASE_DIR, MIDDLEWARE


sentry_sdk.init(
    dsn="https://918cdbc4393a4dc0aa38530f61da9daf@o448987.ingest.sentry.io/5431213",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
# TODO: SECURE_HSTS_SECONDS

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# TODO: use posgres

# TODO
BASIC_TOKENS = [
    'debug:test',
]
