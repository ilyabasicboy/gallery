from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from gallery_new.api.models import Token

import json
from PIL import Image


class TestViews(APITestCase):

    def setUp(self):
        self.client = APIClient()
        user, created = User.objects.get_or_create(username='test')
        token, created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(token.key))

    def test_files_GET(self):
        url = reverse('files')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_files_upload_POST(self):
        url = reverse('files_upload')
        file = Image.new("RGBA", (200, 200), (255,0,0,0))
        data = {
            'media_type': 'image/png',
            'file': file
        }
        response = self.client.get(url, data)
        print(response.reason)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
