from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from pathlib import Path

from .models import MediaFile, EntityFile, Token
from .utils.validators import MimeTypeValidator


class SlotSerializer(serializers.HyperlinkedModelSerializer):

    size = serializers.IntegerField(source='entity_file.size', default=0)
    hash = serializers.CharField(source='entity_file.hash')

    class Meta:
        model = MediaFile
        fields = ['size', 'hash']


class FilesSerializer(serializers.HyperlinkedModelSerializer):

    hash = serializers.ReadOnlyField(source='entity_file.hash')
    media_type = serializers.ReadOnlyField(source='entity_file.media_type')
    file = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    size = serializers.IntegerField(source='entity_file.size')
    name = serializers.CharField(source='entity_file.name')

    class Meta:
        model = MediaFile
        fields = ['id', 'size', 'media_type', 'name', 'title', 'file', 'created_at', 'hash', 'thumbnail']

    def get_file(self, media_file):
        return str(Path(settings.STATIC_LINK, media_file.title, media_file.entity_file.name))

    def get_thumbnail(self, media_file, *args, **kwargs):

        """ Customize thumbnail field """

        thumbnail_info = {
            'url': str(Path(settings.STATIC_LINK, media_file.title, 'thumbnail_%s' % media_file.entity_file.name)),
            'width': settings.DEFAULT_THUMB_SIZE_TUPLE[0],
            'height': settings.DEFAULT_THUMB_SIZE_TUPLE[1],
        }
        return thumbnail_info


class AvatarSerializer(FilesSerializer):

    """ Modified FilesSerializer for avatar list """

    thumbnails = serializers.SerializerMethodField()
    title = serializers.ReadOnlyField()
    id = serializers.IntegerField(required=True)
    size = serializers.IntegerField(source='entity_file.size')
    name = serializers.CharField(source='entity_file.name')

    class Meta:
        model = MediaFile
        fields = ['id', 'size', 'media_type', 'name', 'title', 'file', 'created_at', 'hash', 'thumbnail', 'thumbnails', 'is_avatar']

    def get_thumbnails(self, media_file, *args, **kwargs):

        """ Customize thumbnails field """

        thumbnails_info = []
        if media_file.avatar_thumbs:
            thumbnails_info = [
                {
                    'url': str(Path(settings.STATIC_LINK, media_file.title, '%s_%s.webp' % (thumbnail.side_size, media_file.entity_file.name))),
                    'width': thumbnail.side_size,
                    'height': thumbnail.side_size,
                } for thumbnail in media_file.entity_file.thumbnail_set.filter(is_avatar=True)
            ]
        return thumbnails_info


class FilesUploadSerializer(serializers.HyperlinkedModelSerializer):

    hash = serializers.ReadOnlyField()
    media_type = serializers.CharField(help_text=u'Example: image/png', validators=[MimeTypeValidator()])
    avatar_thumbs = serializers.BooleanField()
    metadata = serializers.JSONField(required=False)

    class Meta:
        model = EntityFile
        fields = ['file', 'size', 'hash', 'media_type', 'avatar_thumbs', 'metadata',]


class XmppCodeSerializer(serializers.Serializer):

    jid = serializers.CharField(required=True)
    type = serializers.CharField(required=False, initial='message')


class XmppAuthSerializer(serializers.HyperlinkedModelSerializer):

    jid = serializers.CharField(source='user.username', required=True)
    code = serializers.IntegerField(required=True)

    class Meta:
        model = Token

        fields = ['jid', 'code', 'device', 'client']


class TokensSerializer(serializers.HyperlinkedModelSerializer):

    token_id = serializers.IntegerField(source='id', required=True)

    class Meta:
        model = Token
        fields = ['token_id', 'device', 'client', 'created_at', 'expires']


class AccountListSerializer(serializers.HyperlinkedModelSerializer):

    jid = serializers.ReadOnlyField(source='username')
    quota = serializers.ReadOnlyField(source='quota.size', read_only=True)
    used = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['jid', 'quota', 'used']

    def get_used(self, user):
        return user.quota.get_quota_used()


class AccountSerializer(serializers.HyperlinkedModelSerializer):

    jid = serializers.CharField(source='username', required=True)
    code = serializers.CharField(source='verification_code__value', required=True)

    class Meta:
        model = User
        fields = ['jid', 'code']
