from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from typing import Tuple
import av
from ..models import EntityFile, Thumbnail, MediaFile
from pathlib import Path
from django.conf import settings
from .simlinks import create_symlink


def create_image_thumb(upload: str, name: str) -> Tuple[str, ContentFile]:
    image = Image.open(upload)
    im = ImageOps.fit(image, settings.DEFAULT_THUMB_SIZE_TUPLE)
    thumb_io = BytesIO()
    im.save(thumb_io, image.format, quality=60)
    return "thumb_{}".format(name), ContentFile(thumb_io.getvalue(), name)


def create_video_thumb(upload: str, name: str) -> Tuple[str, ContentFile]:
    container = av.open(upload)
    frame = next(container.decode(video=0))
    fimage = frame.to_image()
    im = ImageOps.fit(fimage, settings.DEFAULT_THUMB_SIZE_TUPLE)
    thumb_io = BytesIO()
    im.save(thumb_io, im.format, quality=60)
    return "thumb_{}".format(name), ContentFile(thumb_io.getvalue(), name)


def create_avatar_thumbs(entity_file: EntityFile, media_file: MediaFile) -> list:
    name = Path(entity_file.file.name).stem
    symlink_name = Path(media_file.name).stem
    image = Image.open(entity_file.file)
    for size in settings.THUMBS_SIZE_LIST:
        if image.size[0] > size:
            thumbnail, created = entity_file.thumbnail_set.get_or_create(
                is_avatar=True,
                side_size=size
            )
            if created:
                thumbnail.file.save(*resize_avatar(image, name, size))
            create_symlink(
                path=thumbnail.file.path,
                file_name="{}_{}.webp".format(size, symlink_name),
                title=media_file.title,
            )


def resize_avatar(image: Image, name: str, size: int) -> Tuple[str, ContentFile]:
    img = image.resize((size, size))
    thumb_io = BytesIO()
    img.save(thumb_io, 'webp', quality=100, lossless=True, method=1)
    return '{}_{}'.format(size, name), ContentFile(thumb_io.getvalue(), name)


def create_thumbnails(media_file: MediaFile, is_avatar: bool = False, avatar_thumbs: bool = False) -> None:

    """ Create thumbnails and symlinks for media file """

    # try, except for using threading
    try:
        entity_file = media_file.entity_file
        media_type, format = media_file.media_type.split('/')

        if media_type in ['image', 'video']:

            thumbnail, created = Thumbnail.objects.get_or_create(
                entity_file=entity_file,
                is_avatar=False
            )

            if created:
                if media_type == 'image':
                    thumb = create_image_thumb(entity_file.file, entity_file.get_filename())
                else:
                    thumb = create_video_thumb(entity_file.file, entity_file.get_filename())
                thumbnail.file.save(*thumb)

            create_symlink(
                path=thumbnail.file.path,
                file_name='thumb_{}'.format(media_file.name),
                title=media_file.title,
            )

        if is_avatar and avatar_thumbs and media_type == 'image':
            create_avatar_thumbs(entity_file, media_file)
    except Exception as e:
        print(e)


def crop_avatar(file: Image) -> dict:
    image = Image.open(file)
    width, height = image.size
    new_size = width
    if not width == height or width >= settings.MAX_AVATAR_SIZE:
        max_dim, min_dim, = (width, height) if width > height else (height, width)
        new_size = settings.MAX_AVATAR_SIZE if max_dim >= settings.MAX_AVATAR_SIZE else min_dim
        img = ImageOps.fit(image, (new_size, new_size))
        img.save(file.temporary_file_path())
    return {
        "max_size": new_size
    }
