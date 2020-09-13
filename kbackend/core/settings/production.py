import os

from core.settings.common import *
from core.settings.common import BASE_DIR, MIDDLEWARE


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# TODO: use posgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# TODO
BASIC_TOKENS = [
    'debug:test',
]
