from API_Apuestas_Deportivas.settings import *

SECRET_KEY = 'cncefjio434klcvjdvfsdop'
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

