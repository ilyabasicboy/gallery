import os
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.conf import settings
from django.urls import reverse

from .cache_quota import UserCacheQuota
from .utils.thumbnails import crop_avatar
from .utils.exceptions import QuotaExceeded, TooManyRequests, LargeFileSize


class LimitSizeFileUploadHandler(FileUploadHandler):
    file_counter = 0

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.user_quota = self.request.user.quota.size
        self.user_quota_used = self.request.user.quota.used
        self.file = TemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)
        self.request_size = self.request.POST.get('size')
        self.is_avatar = self.request.path == reverse('avatar_upload')
        self.is_image = "image" in self.file.content_type
        self._cache = UserCacheQuota(self.request.user.username, self.user_quota_used)

        if self._cache.files_counter > settings.FILES_LIMIT:
            raise TooManyRequests

        self.file_counter += 1
        if self.file_counter > 10:
            raise StopUpload(True)

        if self.request_size:
            if not self.request.user.quota.quota_available(user=self.request.user, size=self.request_size):
                raise QuotaExceeded

    def receive_data_chunk(self, raw_data, start):
        if len(raw_data) + start + self._cache.quota_used > self.user_quota:
            raise QuotaExceeded
        if len(raw_data) + start > settings.MAX_FILE_SIZE:
            raise LargeFileSize
        if len(raw_data) + start + self.user_quota_used > settings.DEFAULT_QUOTA_OVERSIZE + self.user_quota:
            raise QuotaExceeded
        self.file.write(raw_data)

    def file_complete(self, file_size):
        self.request.user.quota.update_quota_used()
        self.file.seek(0)
        self.file.size = file_size
        self._cache.quota_used = self.file.size
        os.chmod(self.file.temporary_file_path(), 0o644)
        if self.is_avatar:
            if self.is_image:
                avatar = crop_avatar(self.file)
                self.request.META['max_size'] = avatar.get('max_size')
            else:
                raise StopUpload(True)
        return self.file
