import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '0ziz(40_ztqj!#$@^^*+7^=0sbr5e7-f6^8g*ksu$45&4n8^$r'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gallery_new.api',
    "django_jsonfield_backport",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gallery_new.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'gallery_new.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

# -------- AUTH ---------#
XMPP_LOGIN = ''
XMPP_PASS = ''
VERIFICATION_CODE_LIFETIME = 90
TOKEN_LIFETIME = 3600 * 24

# -------- DRF ---------#

INSTALLED_APPS += ['rest_framework',]

REST_FRAMEWORK = {
    'ORDERING_PARAM': 'order_by',
}

# -------- FILES --------- #

STATIC_LINK = 'https://127.0.0.1/gallery/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploaded')
ORIGINAL_FILE_DIR = 'originals'

FILE_UPLOAD_HANDLERS = [
    'gallery_new.api.limit_size_fileupload_handler.LimitSizeFileUploadHandler',
]

SYMLINKS_DIR = 'symlinks'

# THUMBS
THUMBNAIL_FILE_DIR = 'thumbnails'
DEFAULT_THUMB_SIZE = 256
DEFAULT_THUMB_SIZE_TUPLE = DEFAULT_THUMB_SIZE if isinstance(DEFAULT_THUMB_SIZE, tuple) else (DEFAULT_THUMB_SIZE, DEFAULT_THUMB_SIZE)
THUMBS_SIZE_LIST = (32, 48, 64, 96, 128, 192, 256, 384, 512, 768)
MAX_AVATAR_SIZE = 1536

# QUOTA
MAX_FILE_SIZE = 30000000  # 30 MB
DEFAULT_QUOTA_SIZE = 100000  # 100 MB
DEFAULT_QUOTA_OVERSIZE = 1000000  # 1 MB
FILES_LIMIT = 10  # Limit the number of simultaneous file transfers
TIME_WINDOW = 10  # Limit the frequency of file transfers: FILES_LIMIT per TIME_WINDOW
