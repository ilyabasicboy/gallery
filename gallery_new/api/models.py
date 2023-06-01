from django.db import models
from django_jsonfield_backport.models import JSONField
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from uuid import uuid4

from .utils.generators import get_upload_entity, get_upload_thumb, get_token_lifetime, get_code_lifetime, generate_uuid, generate_title
from .utils.validators import MimeTypeValidator

import os


class EntityFile(models.Model):

    file = models.FileField(upload_to=get_upload_entity)
    hash = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.get_filename()

    def get_filename(self):
        return os.path.basename(self.file.file.name)


class MediaFile(models.Model):

    entity_file = models.ForeignKey(EntityFile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar_thumbs = models.BooleanField(default=False)
    size = models.IntegerField(blank=True)
    media_type = models.CharField(
        max_length=255,
        validators=[MimeTypeValidator()]
    )
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(
        max_length=255,
        unique=True,
        default=generate_title
    )
    metadata = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_avatar = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Thumbnail(models.Model):

    entity_file = models.ForeignKey(EntityFile, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_upload_thumb)
    is_avatar = models.BooleanField(default=False)
    side_size = models.IntegerField(default=settings.DEFAULT_THUMB_SIZE_TUPLE[0])

    def __str__(self):
        return self.get_filename()

    def get_filename(self):
        return os.path.basename(self.file.file.name)


class Quota(models.Model):
    class Meta:
        ordering = ['user__username']

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='quota')

    size = models.IntegerField(default=settings.DEFAULT_QUOTA_SIZE, null=True, blank=True)
    used = models.IntegerField(default=0, null=True, blank=True)

    def get_quota_used(self):
        summ = 0
        mediafiles = MediaFile.objects.filter(user=self.user).aggregate(models.Sum('size'))
        if mediafiles.get('size__sum'):
            summ = mediafiles.get('size__sum')
        return summ

    def update_quota_used(self):
        self.quota_used = self.get_quota_used()
        self.save()

    def update_quota_value(self, value):
        self.size = value
        self.save()

    def quota_available(self, size):
        return int(size) < (self.size - self.get_quota_used())

    def __str__(self):
        return self.user.username


class Token(models.Model):

    key = models.CharField(max_length=255, editable=False, default=generate_uuid)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.CharField(max_length=255, null=True, blank=True)
    client = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    expires = models.DateTimeField(default=get_token_lifetime)

    def __str__(self):
        return self.user.username


class VerificationCode(models.Model):
    value = models.IntegerField(blank=True, unique=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_code')
    expires = models.DateTimeField(default=get_code_lifetime)

    def __str__(self):
        return str(self.expires)

    def check_expires(self):
        if timezone.now() > self.expires:
            self.delete()
            return False
        return True
