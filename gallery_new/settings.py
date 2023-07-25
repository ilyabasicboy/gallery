from .generic_settings import *


DEBUG = True


ALLOWED_HOSTS = ['*']

STATIC_LINK = 'https://127.0.0.1/gallery/media/'


MAX_FILE_SIZE = 106214400
DEFAULT_SOFT_QUOTA_SIZE = 100000000
DEFAULT_HARD_QUOTA_SIZE = 110000000
DEFAULT_QUOTA_SIZE = 10
VERIFICATION_CODE_LIFETIME = 600

FILE_UPLOAD_PERMISSIONS = 0o644

WHITE_LIST = []
BLACK_LIST = []

API_KEY_IP = {'127.0.0.1': '1234567'}

TIME_ZONE = 'Asia/Yekaterinburg'