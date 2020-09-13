from core.settings.common import *
from core.settings.common import BASE_DIR


SECRET_KEY = 'n+q%w90_u&f@1gvxeg068u=!xjpep+i#t*6s-6ml+q*w(#qc7$'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

BASIC_TOKENS = [
    'debug:token',
]
