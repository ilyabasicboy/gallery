from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from pathlib import Path

from .models import MediaFile, EntityFile, Token
from .utils.validators import MimeTypeValidator
from .utils.generators import get_file_url


class SlotSerializer(serializers.HyperlinkedModelSerializer):

    hash = serializers.CharField(source='entity_file.hash')
    name = serializers.CharField(required=True)
    size = serializers.IntegerField(required=True)

    class Meta:
        model = MediaFile
        fields = ['size', 'hash', 'name']


class FilesSerializer(serializers.HyperlinkedModelSerializer):

    hash = serializers.ReadOnlyField(source='entity_file.hash')
    file = serializers.SerializerMethodField(method_name='get_file_url')
    thumbnail = serializers.SerializerMethodField(read_only=True)
    slot_id = serializers.ReadOnlyField(source='title')

    class Meta:
        model = MediaFile
        fields = ['id', 'size', 'media_type', 'name', 'slot_id', 'file', 'created_at', 'hash', 'thumbnail']

    def get_file_url(self, media_file):
        return get_file_url(media_file.title, media_file.name)

    def get_thumbnail(self, media_file, *args, **kwargs):

        """ Customize thumbnail field """

        thumbnail_info = {
            'url': get_file_url(media_file.title, 'thumb_%s' % media_file.name),
            'width': settings.DEFAULT_THUMB_SIZE_TUPLE[0],
            'height': settings.DEFAULT_THUMB_SIZE_TUPLE[1],
        }
        return thumbnail_info


class AvatarSerializer(FilesSerializer):

    """ Modified FilesSerializer for avatar list """

    thumbnails = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(required=True)
    media_type = serializers.CharField(required=False)
    slot_id = serializers.ReadOnlyField(source='title')

    class Meta:
        model = MediaFile
        fields = ['id', 'size', 'media_type', 'name', 'slot_id', 'file', 'created_at', 'hash', 'thumbnail', 'thumbnails', 'is_avatar']

    def get_thumbnails(self, media_file, *args, **kwargs):

        """ Customize thumbnails field """

        thumbnails_info = []
        if media_file.avatar_thumbs:
            thumb_name = Path(media_file.name).stem
            thumbnails_info = [
                {
                    'url': get_file_url(media_file.title, '%s_%s.webp' % (thumbnail.side_size, thumb_name)),
                    'width': thumbnail.side_size,
                    'height': thumbnail.side_size,
                } for thumbnail in media_file.entity_file.thumbnail_set.filter(is_avatar=True)
            ]
        return thumbnails_info


class FilesUploadSerializer(serializers.HyperlinkedModelSerializer):

    hash = serializers.ReadOnlyField()
    media_type = serializers.CharField(help_text=u'Example: image/png', validators=[MimeTypeValidator()])
    size = serializers.IntegerField(required=False)
    create_thumbnails = serializers.BooleanField(default=True)
    metadata = serializers.JSONField(required=False)

    class Meta:
        model = EntityFile
        fields = ['file', 'size', 'hash', 'media_type', 'create_thumbnails', 'metadata',]


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
    quota = serializers.ReadOnlyField(source='quota.get_size', read_only=True)
    used = serializers.ReadOnlyField(source='quota.used')

    class Meta:
        model = User
        fields = ['jid', 'quota', 'used']


class AccountSerializer(serializers.HyperlinkedModelSerializer):

    jid = serializers.CharField(source='username', required=True)
    code = serializers.CharField(source='verification_code__value', required=True)

    class Meta:
        model = User
        fields = ['jid', 'code']
