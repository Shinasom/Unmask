# core/settings.py

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^v=%8#(nml1s8!x5cwi_tz%r%+d4tb%9s*w$m=pn5(!*(1q+mu"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.42', 'localhost', '127.0.0.1','*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'channels',  # ADD THIS

    # My Apps
    'users.apps.UsersConfig',
    'photos.apps.PhotosConfig',
    'interactions.apps.InteractionsConfig',
    'direct_chat.apps.DirectChatConfig',  # ADD THIS
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # <-- Add this here
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sec_ur_privacy',
        'USER': 'secuser',
        'PASSWORD': 'mainproject',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- CUSTOM PROJECT SETTINGS ---

# --- AUTHENTICATION ---
# This is the CRITICAL line that tells Django to use our custom user model.
AUTH_USER_MODEL = 'users.CustomUser'

# --- EMAIL (FOR DEVELOPMENT) ---
# This setting tells Django to print emails to the console instead of sending them.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- STATIC & MEDIA FILES ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- CORS (FOR REACT FRONTEND) ---
# For development, we can allow all origins. In production, we'd lock this down.
# --- CORS (FOR REACT FRONTEND) ---
# Whitelist the frontend origins that are allowed to make requests to this API
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://192.168.1.42:3000",
#     "http://127.0.0.1:3000",
# ]
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

# --- DJANGO REST FRAMEWORK ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # Token lasts 24 hours
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Refresh token lasts 7 days
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# --- LOGGING CONFIGURATION ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            # --- THIS IS THE CHANGE ---
            "level": "WARNING", # Was "INFO", change to "WARNING"
            # --- END OF CHANGE ---
            "propagate": False,
        },
        "users": { # Logger for your 'users' app
            "handlers": ["console"],
            "level": "DEBUG", # Show everything from DEBUG level up
            "propagate": False,
        },
        "photos": { # Logger for your 'photos' app
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "interactions": { # Logger for your 'interactions' app
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'SEC-UR Privacy API',
    'DESCRIPTION': 'Privacy-first photo sharing platform with consent management',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'COMPONENT_SPLIT_REQUEST': True
}


# --- ASGI / CHANNELS CONFIGURATION ---
ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}