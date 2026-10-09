from .base import *

DEBUG = False

if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'foodshare_ai'),
            'USER': os.getenv('POSTGRES_USER', 'foodshare_user'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'change-me'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
