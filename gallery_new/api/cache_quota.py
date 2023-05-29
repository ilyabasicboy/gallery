from django.core.cache import caches
from django.conf import settings

cache = caches['default']


class UserCacheQuota:

    def __init__(self, user, quota_used):
        self.files_key = 'f_{}'.format(user)
        self.quota_key = 'q_{}'.format(user)
        cache.set(self.quota_key, quota_used)
        self.increase_counter()

    def increase_counter(self):
        if not cache.get(self.files_key):
            cache.set(self.files_key, 1, timeout=settings.TIME_WINDOW)
        else:
            cache.incr(self.files_key, 1)

    @property
    def files_counter(self):
        counter = cache.get(self.files_key)
        return counter if counter else 0

    @property
    def quota_used(self):
        return cache.get(self.quota_key)

    @quota_used.setter
    def quota_used(self, value):
        cache.set(self.quota_key, self.quota_used + value)
