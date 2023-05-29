from django.db.models import Sum
from django.conf import settings
from django.db.models.functions import Coalesce
from pathlib import Path
from gallery_new.api.models import MediaFile, Quota
from .exceptions import MailformedData

import json


def file_upload_response(
        media_file: MediaFile,
        is_avatar: bool = False,
        avatar_thumbs: bool = False,
        max_size: int = settings.MAX_AVATAR_SIZE
) -> dict:

    response = {
        'id': media_file.id,
        'size': media_file.size,
        'media_type': media_file.media_type,
        'name': media_file.name,
        'title': media_file.title,
        'created_at': media_file.created_at,
        'file': str(Path(settings.STATIC_LINK, media_file.title, media_file.name)),
        'hash': media_file.entity_file.hash,
        'thumbnail': {
            'url': str(Path(settings.STATIC_LINK, media_file.title, 'thumbnail_%s' % media_file.name)),
            'width': settings.DEFAULT_THUMB_SIZE_TUPLE[0],
            'height': settings.DEFAULT_THUMB_SIZE_TUPLE[1],
        },
        'used': media_file.user.quota.get_quota_used(),
        'quota': media_file.user.quota.size
    }

    # optional attrs
    if media_file.metadata:
        metadata = json.loads(media_file.metadata)
        if metadata:
            response['metadata'] = metadata

    if is_avatar:
        response['is_avatar'] = True

        if avatar_thumbs:
            thumb_name = Path(media_file.name).stem
            response['thumbnails'] = [
                {
                    'url': str(Path(settings.STATIC_LINK, media_file.title, '%s_%s.webp' % (size, thumb_name))),
                    'width': size,
                    'height': size,
                } for size in settings.THUMBS_SIZE_LIST if size < max_size
            ]

    return response


def get_quota_response(quota: Quota) -> dict:
    response = {
        'quota': quota.size,
        'used': quota.get_quota_used()
    }
    return response


def stats_response(media_files, quota: int) -> dict:

    images = media_files.filter(media_type__startswith='image')
    videos = media_files.filter(media_type__startswith='video')
    voices = media_files.filter(media_type__startswith='voice')
    files = media_files.filter(media_type__startswith='file')

    response = {
        'images': {
            'count': images.count(),
            'used': images.aggregate(size=Coalesce(Sum('size'), 0)).get('size')
        },
        'videos': {
            'count': videos.count(),
            'used': videos.aggregate(size=Coalesce(Sum('size'), 0)).get('size')
        },
        'voices': {
            'count': voices.count(),
            'used': voices.aggregate(size=Coalesce(Sum('size'), 0)).get('size')
        },
        'files': {
            'count': files.count(),
            'used': files.aggregate(size=Coalesce(Sum('size'), 0)).get('size')
        },
        'total': {
            'count': media_files.count(),
            'used': media_files.aggregate(size=Coalesce(Sum('size'), 0)).get('size')
        },
        'quota': quota
    }

    return response


# ----- ERROR RESPONSES ------

def serialize_data(serializer):
    if not serializer.is_valid(raise_exception=True):
        raise MailformedData
    return serializer.data


