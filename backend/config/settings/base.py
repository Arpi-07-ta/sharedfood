import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change-me-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()
]
APP_ENV = os.getenv('APP_ENV', 'development')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'apps.accounts',
    'apps.donations',
    'apps.matching',
    'apps.tracking',
    'apps.notifications',
    'apps.feedback',
    'apps.fraud_detection',
    'apps.analytics',
    'apps.ai_engine',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
PRIVATE_UPLOAD_ROOT = BASE_DIR / 'private_uploads'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

MATCHING_WEIGHTS = {
    'distance': float(os.getenv('MATCHING_WEIGHT_DISTANCE', '0.30')),
    'food_compatibility': float(os.getenv('MATCHING_WEIGHT_FOOD_COMPATIBILITY', '0.20')),
    'urgency': float(os.getenv('MATCHING_WEIGHT_URGENCY', '0.20')),
    'capacity': float(os.getenv('MATCHING_WEIGHT_CAPACITY', '0.15')),
    'current_demand': float(os.getenv('MATCHING_WEIGHT_CURRENT_DEMAND', '0.10')),
    'reliability': float(os.getenv('MATCHING_WEIGHT_RELIABILITY', '0.05')),
}
MATCHING_MAX_DISTANCE_KM = float(os.getenv('MATCHING_MAX_DISTANCE_KM', '100'))
MATCHING_URGENCY_HORIZON_HOURS = float(os.getenv('MATCHING_URGENCY_HORIZON_HOURS', '72'))

FRAUD_RISK_THRESHOLDS = {
    'medium': int(os.getenv('FRAUD_RISK_MEDIUM_THRESHOLD', '25')),
    'high': int(os.getenv('FRAUD_RISK_HIGH_THRESHOLD', '55')),
    'critical': int(os.getenv('FRAUD_RISK_CRITICAL_THRESHOLD', '80')),
}
FRAUD_MAX_DONATION_KG = float(os.getenv('FRAUD_MAX_DONATION_KG', '500'))
FRAUD_DUPLICATE_WINDOW_HOURS = int(os.getenv('FRAUD_DUPLICATE_WINDOW_HOURS', '48'))
FRAUD_SIMILARITY_THRESHOLD = float(os.getenv('FRAUD_SIMILARITY_THRESHOLD', '0.85'))
FRAUD_DUPLICATE_QUANTITY_DELTA = float(os.getenv('FRAUD_DUPLICATE_QUANTITY_DELTA', '0.25'))
FRAUD_CANCELLATION_WINDOW_DAYS = int(os.getenv('FRAUD_CANCELLATION_WINDOW_DAYS', '30'))
FRAUD_REPEATED_CANCELLATION_COUNT = int(os.getenv('FRAUD_REPEATED_CANCELLATION_COUNT', '3'))
FRAUD_SUBMISSION_WINDOW_HOURS = int(os.getenv('FRAUD_SUBMISSION_WINDOW_HOURS', '24'))
FRAUD_FREQUENT_SUBMISSION_COUNT = int(os.getenv('FRAUD_FREQUENT_SUBMISSION_COUNT', '10'))
FRAUD_ABNORMAL_ACTIVITY_WINDOW_DAYS = int(os.getenv('FRAUD_ABNORMAL_ACTIVITY_WINDOW_DAYS', '7'))
FRAUD_ABNORMAL_ACTIVITY_COUNT = int(os.getenv('FRAUD_ABNORMAL_ACTIVITY_COUNT', '20'))
FRAUD_COMPLAINT_WINDOW_DAYS = int(os.getenv('FRAUD_COMPLAINT_WINDOW_DAYS', '90'))
FRAUD_REPEATED_COMPLAINT_COUNT = int(os.getenv('FRAUD_REPEATED_COMPLAINT_COUNT', '3'))
FRAUD_POINTS_UNREALISTIC_QUANTITY = int(os.getenv('FRAUD_POINTS_UNREALISTIC_QUANTITY', '40'))
FRAUD_POINTS_SIMILAR_DONATION = int(os.getenv('FRAUD_POINTS_SIMILAR_DONATION', '35'))
FRAUD_POINTS_REPEATED_CANCELLATIONS = int(os.getenv('FRAUD_POINTS_REPEATED_CANCELLATIONS', '30'))
FRAUD_POINTS_FREQUENT_SUBMISSIONS = int(os.getenv('FRAUD_POINTS_FREQUENT_SUBMISSIONS', '20'))
FRAUD_POINTS_ABNORMAL_ACTIVITY = int(os.getenv('FRAUD_POINTS_ABNORMAL_ACTIVITY', '25'))
FRAUD_POINTS_REPEATED_COMPLAINTS = int(os.getenv('FRAUD_POINTS_REPEATED_COMPLAINTS', '35'))

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': os.getenv('JWT_ALGORITHM', 'HS256'),
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', 'replace-with-jwt-secret-key'),
}

CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if origin.strip()
]

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True, parents=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

AUTH_USER_MODEL = 'accounts.User'
