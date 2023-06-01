from pathlib import Path
from datetime import timedelta, datetime
from django.conf import settings
from django.utils import timezone
from uuid import uuid4
from urllib.parse import urljoin

import hashlib
import string
import random
import os


def generate_uuid():
    return str(uuid4())


def get_file_url(*path):

    """ generate correctly url """

    return urljoin(settings.STATIC_LINK, str(Path(*path)))


def get_upload_entity(instance, filename):
    """ Generate path to upload for entity file """
    return str(Path(settings.ORIGINAL_FILE_DIR, instance.hash[:3], instance.hash[3:6], instance.hash[6:]))


def get_upload_thumb(instance, filename):
    """ Generate path to upload for thumbnail """
    return str(Path(settings.THUMBNAIL_FILE_DIR, instance.entity_file.hash[:3], instance.entity_file.hash[3:6], filename))


def hash_md5(file, blocksize: int = 8192) -> str:
    m = hashlib.md5()
    while True:
        buf = file.read(blocksize)
        if not buf:
            break
        m.update(buf)
    return m.hexdigest()


def generate_title(size: int = 12) -> str:
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(size))


def generate_code(size: int = 6) -> str:
    return ''.join(random.choice(string.digits[1:]) for _ in range(size))


def get_token_lifetime() -> datetime:
    return timezone.now() + timedelta(seconds=settings.TOKEN_LIFETIME)


def get_code_lifetime() -> datetime:
    return timezone.now() + timedelta(seconds=settings.VERIFICATION_CODE_LIFETIME)


def get_title_from_path(path):

    """
    returns media file title
    Example:
        path: https:/domain/gallery/media/JyFo5UscmKBj/file.jpg
        result: JyFo5UscmKBj
    """

    try:
        dirname = os.path.dirname(path)
        return Path(dirname).name
    except:
        return ''
