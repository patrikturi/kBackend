from core.settings.common import *  # noqa: F401, F403


SECRET_KEY = 'n+q%w90_u&f@1gvxeg068u=!xjpep+i#t*6s-6ml+q*w(#qc7$'

DEBUG = True
IS_TEST = True

BASIC_TOKENS = [
    'debug:token',
]

CORS_ALLOW_ALL_ORIGINS = True

# Tests run a lot quicker with this password hasher
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
