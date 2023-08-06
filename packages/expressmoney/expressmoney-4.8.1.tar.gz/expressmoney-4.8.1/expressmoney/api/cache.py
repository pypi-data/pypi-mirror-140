import os

from django.contrib.auth import get_user_model
from django.core.cache import cache

__all__ = ('CacheMixin', 'CacheObjectMixin')

from expressmoney.api.utils import log

User = get_user_model()


class FlushCache:
    """"Delete cache for all API points"""
    def __init__(self, user: User):
        self._user = user
        self._memory_cache = None

    @log
    def flush_cache(self):
        self._memory_cache = None
        cache.delete(self._cache_key)

    @property
    def _cache_key(self):
        return getattr(self._user, 'id')


class BaseCacheMixin:
    _cache_period: int = None

    @property
    def _cache_key(self):
        return getattr(self._user, 'id')

    @property
    def _data_key(self):
        return self._service_point.id

    @property
    def _cache(self):
        if self._memory_cache is None:
            all_cache_data = cache.get(self._cache_key)
            self._memory_cache = all_cache_data.get(self._data_key) if all_cache_data else None
            if os.getenv('IS_ENABLE_API_LOG') and self._memory_cache is not None:
                print(f'GET REDIS {self}')
        return self._memory_cache

    @_cache.setter
    def _cache(self, value: any):
        if value is not None:
            data = cache.get(self._cache_key)
            ext_data = {f'{self._data_key}': value}
            data = dict(**data, **ext_data) if data else ext_data
            cache.set(self._cache_key, data, self._cache_period)
            self._memory_cache = value

    @log
    def flush_cache(self):
        """Delete cache for only current service point"""
        self._memory_cache = None
        data = cache.get(self._cache_key)
        if data:
            data.pop(self._data_key, False)
            cache.set(self._cache_key, data, self._cache_period)


class CacheMixin(BaseCacheMixin):

    def __init__(self, user: User):
        self._user = user
        self._memory_cache = None
        super().__init__(user)

    def _get(self) -> dict:
        if self._cache is not None:
            return self._cache
        return super()._get()

    def _post(self, payload: dict):
        self.flush_cache()
        super()._post(payload)

    def _post_file(self, file, file_name, type_):
        self.flush_cache()
        super()._post_file(file, file_name, type_)


class CacheObjectMixin(BaseCacheMixin):

    def __init__(self, user: User, lookup_field_value: str = None):
        self._user = user
        self._memory_cache = None
        super().__init__(user, lookup_field_value)

    def _get(self) -> dict:
        if self._cache is not None:
            return self._cache
        return super()._get()

    def _put(self, payload: dict):
        self.flush_cache()
        super()._put(payload)
