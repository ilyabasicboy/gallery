from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied, NotFound

from django.contrib.auth.models import User
from django.conf import settings
from xmpp.protocol import JID
from uuid import uuid4
from threading import Thread

from .models import EntityFile, MediaFile, Quota, Token, VerificationCode
from .serializers import FilesSerializer, FilesUploadSerializer, SlotSerializer, XmppAuthSerializer,\
    TokensSerializer, AccountSerializer, XmppCodeSerializer, AvatarSerializer, AccountListSerializer
from .backends import CustomFilterBackend, CustomPagination, CustomTokenAuth

from .utils.other import is_blacklisted_or_not_whitelisted, send_code
from .utils.generators import hash_md5, generate_code, get_title_from_path
from .utils.thumbnails import create_thumbnails
from .utils.responses import file_upload_response, get_quota_response, stats_response, serialize_data
from .utils.exceptions import QuotaExceeded, NoFile
from .utils.opengraph import OpenGraph
from .utils.validators import validate_name

import os


class FilesView(ListModelMixin, GenericViewSet):

    """
        Media file list
    """

    http_method_names = ['get', 'delete']
    queryset = MediaFile.objects.all().order_by('-created_at')
    serializer_class = FilesSerializer
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter, CustomFilterBackend]
    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # ------------ FILTER ---------------

    # select parameters for special method
    filter_parameters_DELETE = [
        'id',
        # name of provided param / queryset argument
        ('media_type', 'media_type__contains'),
        ('date_gte', 'created_at__gte'),
        ('date_lte', 'created_at__lte')
    ]
    filter_required_parameters_DELETE = ['id', 'media_type', 'date_gte', 'date_lte']

    filter_parameters = [
        'id',
        ('media_type', 'media_type__contains'),
        ('date_gte', 'created_at__gte'),
        ('date_lte', 'created_at__lte'),
        ('size_lte', 'size__lte'),
        ('size_gte', 'size__gte')
    ]

    def delete(self, request, *args, **kwargs):

        path = request.data.get('file')
        if path:
            # delete using file path
            title = get_title_from_path(path)
            queryset = self.get_queryset().filter(title=title)
        else:
            # delete using filter backend
            queryset = self.filter_queryset(self.get_queryset())

        if not queryset:
            raise NotFound({"status": status.HTTP_404_NOT_FOUND, "error": "Files does not exist"})

        # Check deleting from storage in api/signals.py
        queryset.delete()
        return Response('Files was delete', status.HTTP_204_NO_CONTENT)


class SlotView(GenericAPIView):

    """
        Check user quota availability
        or create new media file if original file exists
    """
    http_method_names = ['get',]
    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SlotSerializer

    def get(self, request, *args, **kwargs):

        # validate data
        data = serialize_data(self.get_serializer(data=request.data))

        # variables
        entity_file = EntityFile.objects.filter(hash=data.get('hash')).first()
        size = data.get('size')
        name = data.get('name')

        # check user quota
        quota, created = Quota.objects.get_or_create(user=request.user)
        if not quota.quota_available(size):
            raise QuotaExceeded

        if entity_file:
            # create new simlink
            media_file = MediaFile.objects.create(
                entity_file=entity_file,
                user=request.user,
                name=name
            )
            return Response(file_upload_response(media_file), status.HTTP_200_OK)
        else:
            return Response(get_quota_response(quota))


class UploadFileView(CreateAPIView):

    """ Customized to create multiple models on uploading file """

    queryset = EntityFile.objects.all()
    serializer_class = FilesUploadSerializer
    http_method_names = ['post',]
    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        # validate data
        file = request.data.get('file', request.FILES.get('file'))
        if not file:
            raise NoFile
        file.name = validate_name(file.name)
        data = serialize_data(self.get_serializer(data=request.data))

        # variables
        avatar_thumbs = data.get('avatar_thumbs', False)
        size = data.get('size', 0)
        media_type = data.get('media_type', None)
        metadata = data.get('metadata', None)
        max_size = request.META.get('max_size', settings.MAX_AVATAR_SIZE)
        is_avatar = kwargs.get('is_avatar', False)
        file_hash = hash_md5(file)

        # create or find original file
        entity_file = EntityFile.objects.filter(hash=file_hash).first()
        if not entity_file:
            entity_file = EntityFile.objects.create(file=file, hash=file_hash)

        # create media file and symlink
        # Symlink creates in signals
        media_file = MediaFile.objects.create(
            entity_file=entity_file,
            user=request.user,
            metadata=metadata,
            is_avatar=is_avatar,
            avatar_thumbs=avatar_thumbs,
            media_type=media_type,
            size=size,
            name=file.name
        )

        # Create thumbnails using multithreading. Required mimetypes: [image, video]
        Thread(
            target=create_thumbnails,
            args=(media_file,),
            kwargs={
                'is_avatar': is_avatar,
                'avatar_thumbs': avatar_thumbs
            }
        ).start()

        return Response(
            file_upload_response(media_file, is_avatar, avatar_thumbs, max_size),
            status=status.HTTP_201_CREATED
        )


class XmppCodeView(GenericAPIView):

    serializer_class = XmppCodeSerializer

    def post(self, request):

        # validate data
        data = serialize_data(self.get_serializer(data=request.data))

        # variables
        jid = data.get('jid')

        code = generate_code()
        confirm_url = request.build_absolute_uri('xmpp_auth')
        stanza_id = uuid4()

        jid_obj = JID(jid)
        bare_jid = jid_obj.getStripped()
        resource = jid_obj.getResource()

        # default stanza type is 'message'
        stanza_type = data.get('type') if data.get('type') else 'message'

        if is_blacklisted_or_not_whitelisted(resource, bare_jid):
            raise PermissionDenied({'status': status.HTTP_403_FORBIDDEN, 'error': 'Access denied'})

        # send code using multithreading
        Thread(
            target=send_code,
            args=(
                settings.XMPP_LOGIN, settings.XMPP_PASS, code,
                jid, stanza_id, stanza_type, confirm_url,
            ),
        ).start()

        # create verification code
        user, created = User.objects.get_or_create(username=bare_jid)
        VerificationCode.objects.create(user=user, value=code)

        return Response({'request_id': stanza_id, 'api_jid': settings.XMPP_LOGIN}, status=status.HTTP_201_CREATED)


class XmppAuthView(CreateAPIView):

    """ Token create view """

    serializer_class = XmppAuthSerializer

    def create(self, request, *args, **kwargs):
        # validate data
        data = serialize_data(self.get_serializer(data=request.data))

        # variables
        jid = data.get('jid')
        code = data.get('code')

        user = User.objects.filter(username=jid).first()
        verification_code = VerificationCode.objects.filter(user=user, value=code).first()

        # check verification code expires
        if verification_code and verification_code.check_expires():
            token = Token.objects.create(user=user, device=data.get('device'), client=data.get('client'))
            headers = self.get_success_headers(data)
            return Response({'token': token.key, 'expires': token.expires}, status=status.HTTP_201_CREATED, headers=headers)
        else:
            raise NotFound({'status': status.HTTP_404_NOT_FOUND, 'error': 'Does not exist'})


class TokensView(ListModelMixin, GenericViewSet):

    """ Token list view"""

    queryset = Token.objects.all()
    serializer_class = TokensSerializer
    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):

        # validate data
        data = serialize_data(self.get_serializer(data=request.data))

        try:
            self.get_queryset().get(id=data.get('token_id')).delete()
        except Token.DoesNotExist:
            raise NotFound({'status': status.HTTP_404_NOT_FOUND, 'error': 'Token does not exist'})

        return Response('Token was delete', status.HTTP_204_NO_CONTENT)


class QuotaView(APIView):

    """ Admin method to change quota """

    http_method_names = ['get', 'put']
    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        quota, created = Quota.objects.get_or_create(user=request.user)
        return Response(get_quota_response(quota))

    def put(self, request):
        value = request.data.get('value')
        quota, created = Quota.objects.get_or_create(user=request.user)
        quota.size = value
        quota.save()
        return Response(get_quota_response(quota))


class AccountListView(ListAPIView):

    queryset = User.objects.all()
    serializer_class = AccountListSerializer
    filter_backends = [OrderingFilter, CustomFilterBackend]
    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    filter_parameters = [('vhost', 'username__endswith'),]


class AccountView(GenericViewSet):

    """
         Account DELETE view.
         If user is not authenticated requires parameters:
            * jid (natalia.barabanschikova@xabber.org)
            * code (484456)
     """


    http_method_names = ['delete',]
    authentication_classes = [CustomTokenAuth]
    serializer_class = AccountSerializer

    def delete(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:

            # validate data
            data = serialize_data(self.get_serializer(data=request.data))

            # get required params
            jid = data.get('jid')
            code = data.get('code')

            try:
                user = User.objects.get(username=jid, verification_code__value=code)
            except User.DoesNotExist:
                raise NotFound({'status':status.HTTP_404_NOT_FOUND, 'error': 'Account does not exist'})

        user.delete()
        return Response('Account was delete', status.HTTP_204_NO_CONTENT)


class AvatarView(ListModelMixin, GenericViewSet):

    queryset = MediaFile.objects.filter(is_avatar=True)
    serializer_class = AvatarSerializer
    filter_backends = [OrderingFilter]
    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):

        # validate data
        data = serialize_data(self.get_serializer(data=request.data))

        try:
            self.get_queryset().get(id=data.get('id')).delete()
        except MediaFile.DoesNotExist:
            raise NotFound({'status': status.HTTP_404_NOT_FOUND, 'error': 'File does not exist'})

        return Response('File was delete', status.HTTP_204_NO_CONTENT)


class StatsView(ListAPIView):

    authentication_classes = [CustomTokenAuth, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        media_files = MediaFile.objects.filter(user=user)
        return Response(stats_response(media_files, user.quota.size))


class OpenGraphView(APIView):

    http_method_names = ['post',]

    def post(self, request):
        url = request.data.get('url')
        result = OpenGraph(url)
        if result.is_valid():
            return Response({'ogp': result.to_html()}, status=201)
        raise NotFound({'error': '404'})
