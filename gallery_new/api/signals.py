from gallery_new.api.models import MediaFile, EntityFile, Quota, Thumbnail
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User

from .utils.generators import hash_md5, generate_title
from .utils.simlinks import create_symlink
from .utils.other import delete_files

from threading import Thread

from pathlib import Path
from shutil import rmtree


@receiver(post_save, sender=MediaFile)
def media_file_post_save(*args, **kwargs):

    """ Create symlinks on media file creating """

    media_file = kwargs.get('instance')
    created = kwargs.get('created')

    if created:
        create_symlink(media_file.entity_file.file.path, media_file.name, media_file.title)


@receiver(pre_save, sender=MediaFile)
def media_file_pre_save(*args, **kwargs):

    """ Generate fields info if it's not provided """

    instance = kwargs.get('instance')

    # generate fields on creation
    if not instance.title:
        instance.title = generate_title(12)
    if not instance.name:
        instance.name = instance.hash[6:]
    if not instance.size:
        instance.size = instance.entity_file.file.file.size


@receiver(post_delete, sender=MediaFile)
def media_file_post_delete(*args, **kwargs):

    """ Delete related files """

    media_file = kwargs.get('instance')

    symlink_path = Path(settings.MEDIA_ROOT, settings.SYMLINKS_DIR, media_file.title)
    if symlink_path.exists():
        rmtree(symlink_path)

    Thread(target=delete_files).start()


@receiver(pre_save, sender=EntityFile)
def entity_file_pre_save(*args, **kwargs):

    """ Generate fields info if it's not provided """

    instance = kwargs.get('instance')

    # Generate hash if it's not provided.
    # WARNING: It's better to provide hash in view.
    # That method can take a lot of time to upload file from storage.
    if not instance.hash:
        file = open(instance.file.path, 'rb')
        instance.hash = hash_md5(file)


@receiver(post_delete, sender=EntityFile)
def entity_file_post_delete(*args, **kwargs):

    """ Delete files and thumbnails from storage"""

    entity_file = kwargs.get('instance')
    file_path = Path(settings.MEDIA_ROOT, settings.ORIGINAL_FILE_DIR, entity_file.hash[:3])
    if file_path.exists():
        rmtree(file_path)


@receiver(post_delete, sender=Thumbnail)
def thumbnail_post_delete(*args, **kwargs):

    """ Delete thumbnails from storage"""

    thumbnail = kwargs.get('instance')
    file_path = Path(settings.MEDIA_ROOT, settings.THUMBNAIL_FILE_DIR, thumbnail.entity_file.hash[:3])
    if file_path.exists():
        rmtree(file_path)


@receiver(post_save, sender=User)
def user_post_save(*args, **kwargs):

    """ Create quota on user creation """

    created = kwargs.get('created')
    user = kwargs.get('instance')

    if created:
        Quota.objects.create(user=user)
