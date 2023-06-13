from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import connection
from django.conf import settings
from django.urls import path, include

from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase
from rest_framework import status

from gallery_new.api.models import Token, MediaFile, EntityFile, VerificationCode
from gallery_new.api.utils.generators import hash_md5

from PIL import Image
from io import BytesIO


class TestViews(APITestCase, URLPatternsTestCase):

    urlpatterns = [
        path('api/', include('gallery_new.api.urls')),
    ]

    def setUp(self):
        self.client = APIClient()
        self.user, created = User.objects.get_or_create(username='test@test')
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token.key))

        # create file for test
        image_io = BytesIO()
        image = Image.new("RGBA", (200, 200), (255, 0, 0, 0))
        image.save(image_io, format='png')
        self.file = ContentFile(image_io.getvalue(), 'test.png')
        self.hash = hash_md5(self.file)

        # test files uploading with oversize
        self.oversize = settings.DEFAULT_QUOTA_SIZE + settings.DEFAULT_QUOTA_OVERSIZE + 1

        # test media_file
        self.entity_file = EntityFile.objects.create(file=self.file, hash=self.hash)
        self.media_file = MediaFile.objects.create(
            entity_file=self.entity_file,
            media_type='image/png',
            size=self.file.size,
            name=self.file.name,
            user=self.user
        )

        # test avatar
        self.avatar = MediaFile.objects.create(
            entity_file=self.entity_file,
            media_type='image/png',
            size=self.file.size,
            name=self.file.name,
            user=self.user,
            is_avatar=True
        )

        # test code
        self.code = VerificationCode.objects.create(value=123456, user=self.user)

    def run(self, *args, **kwargs):
        """
        Customized to close db connections
        because some views use multithreading
        """
        super(TestViews, self).run(*args, **kwargs)
        connection.close()

    def test_files_GET(self):
        url = reverse('files')

        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_files_DELETE(self):
        url = reverse('files')

        response = self.client.delete(url, data={'id': self.media_file.id})
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url, data={'id': 123})
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(url, data={})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_files_upload_POST(self):
        url = reverse('files_upload')

        # Check file uploading if db is not sqlite
        db_engine = settings.DATABASES.get('default', {}).get('ENGINE')
        if not db_engine.endswith('sqlite3'):
            data = {
                'media_type': 'image/png',
                'file': self.file
            }
            response = self.client.post(url, data, format='multipart')
            self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # upload with oversize
        response = self.client.post(url, {'file': self.file, 'size': self.oversize}, format='multipart')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # upload with mailformed data
        response = self.client.post(url, {'file': self.file}, format='multipart')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # upload without file
        response = self.client.post(url)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_slot_GET(self):
        url = reverse('slot')

        data = {
            'size': self.file.size,
            'hash': self.hash,
            'name': self.file.name
        }

        response = self.client.get(url, data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        data['size'] = self.oversize
        response = self.client.get(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_xmpp_code_request_POST(self):
        url = reverse('xmpp_code_request')

        response = self.client.post(url, {'jid': "test@test.test"})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, {})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_xmpp_auth_POST(self):
        url = reverse('xmpp_auth')

        response = self.client.post(url, {})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, {'jid': self.user.username, 'code': self.code.value})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, {'jid': 'test.test.test', 'code': self.code.value})
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tokens_GET(self):
        url = reverse('tokens')

        response = self.client.get(url, {})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_tokens_DELETE(self):
        url = reverse('tokens')

        response = self.client.delete(url, {'token_id': 1234})
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(url, {})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete(url, {'token_id': self.token.id})
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_account_DELETE(self):
        url = reverse('account')

        self.client.credentials()

        response = self.client.delete(url, {"jid": 'test.test.test'})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete(url, {"jid": 'test.test.test', "code": 1234})
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(url, {"jid": self.user.username, "code": self.code.value})
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_quota_GET(self):
        url = reverse('quota')

        response = self.client.get(url, {})
        self.assertEquals(response.status_code, status.HTTP_200_OK)


    def test_quota_PUT(self):
        url = reverse('quota')

        response = self.client.put(url, {})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(url, {'value': 1000000})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_account_list_GET(self):
        url = reverse('account_list')

        response = self.client.get(url, {})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(url, {'vhost': 'test'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_avatar_upload_POST(self):
        url = reverse('avatar_upload')

        # Check file uploading if db is not sqlite
        db_engine = settings.DATABASES.get('default', {}).get('ENGINE')
        if not db_engine.endswith('sqlite3'):
            data = {
                'media_type': 'image/png',
                'file': self.file
            }
            response = self.client.post(url, data, format='multipart')
            self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # # upload with oversize
        # response = self.client.post(url, {'file': self.file, 'size': self.oversize}, format='multipart')
        # self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        #
        # # upload with mailformed data
        # response = self.client.post(url, {'file': self.file}, format='multipart')
        # self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # upload without file
        response = self.client.post(url)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_avatar_GET(self):
        url = reverse('avatar')

        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_avatar_DELETE(self):
        url = reverse('avatar')

        response = self.client.delete(url, data={'id': self.avatar.id})
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url, data={'id': 123})
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(url, data={})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stats_GET(self):
        url = reverse('stats')

        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_opengraph_POST(self):
        url = reverse('opengraph')

        data = {'url': 'https://example.com/'}

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        time.sleep