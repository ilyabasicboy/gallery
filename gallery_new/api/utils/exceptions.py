from rest_framework.exceptions import APIException
from rest_framework import status


class QuotaExceeded(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {
        'status': status.HTTP_403_FORBIDDEN,
        'error': 'Quota exceeded'
    }


class TooManyRequests(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {
        'status': status.HTTP_429_TOO_MANY_REQUESTS,
        'error': 'Too many requests'
    }


class LargeFileSize(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {
        'status': status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        'error': 'Large file size'
    }


class NoFile(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {
        'status': status.HTTP_400_BAD_REQUEST,
        'error': 'No file'
    }


class MailformedData(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {
        'status': status.HTTP_400_BAD_REQUEST,
        'error': 'Mailformed data'
    }
