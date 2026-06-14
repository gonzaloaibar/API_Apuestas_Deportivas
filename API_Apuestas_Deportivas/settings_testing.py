from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-aopapjnl%h1^*4k%si9arx$ix#h-ownt1b)=-tmmpsr)e=*b2d'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3_TESTING',
    }
}
