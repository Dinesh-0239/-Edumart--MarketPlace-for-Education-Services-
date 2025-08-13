"""
Django settings for edumart project.
"""
import os
import random
import string
from pathlib import Path
from decouple import config  # ✅ Added for environment variables

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING
SECRET_KEY = config('SECRET_KEY')  # ✅ Loaded from .env

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = []

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = '/users/login/'

# Razorpay API Keys
RAZORPAY_API_KEY = config('RAZORPAY_API_KEY')  # ✅ Loaded from .env
RAZORPAY_API_SECRET = config('RAZORPAY_API_SECRET')  # ✅ Loaded from .env

SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 86400 * 7
SESSION_COOKIE_SECURE = False

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "edumart_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECRET = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# Application definition
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'channels',

    # Custom apps
    'users',
    'services',
    'bookings',
    'payments',
    'reviews',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom Middlewares
    'edumart.middleware.auth_middleware.AuthMiddleware',
    'edumart.middleware.session_middleware.UniqueSessionMiddleware',
]

ROOT_URLCONF = 'edumart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = "edumart.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

WSGI_APPLICATION = 'edumart.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMTP Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # ✅ Loaded from .env
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # ✅ Loaded from .env
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')
