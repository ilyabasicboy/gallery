from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import connection
from django.conf import settings

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from gallery_new.api.models import Token, MediaFile

from PIL import Image
from io import BytesIO


class TestViews(APITestCase):

    def setUp(self):
        self.client = APIClient()
        user, created = User.objects.get_or_create(username='test')
        token, created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(token.key))

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

    def test_files_upload_POST(self):
        url = reverse('files_upload')

        # create file for test
        image_io = BytesIO()
        image = Image.new("RGBA", (200, 200), (255, 0, 0, 0))
        image.save(image_io, format='png')
        file = ContentFile(image_io.getvalue())

        # Check file uploading if db is not sqlite
        db_engine = settings.DATABASES.get('default', {}).get('ENGINE')
        if not db_engine.endswith('sqlite3'):
            data = {
                'media_type': 'image/png',
                'file': file
            }
            response = self.client.post(url, data, format='multipart')

            self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # upload with mailformed data
        data = {
            'file': file
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # upload without file
        response = self.client.post(url)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)