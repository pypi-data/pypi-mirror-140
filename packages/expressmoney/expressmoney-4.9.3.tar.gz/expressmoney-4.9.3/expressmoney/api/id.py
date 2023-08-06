"""
 Microservice endpoint identifiers
"""
__all__ = ('ID',)


class ID:
    """Base microservice endpoint identifier"""
    def __init__(self, service: str, app: str, view_set: str, action=None) -> None:
        self._service = service
        self._app = app
        self._view_set = view_set
        self._action = action
        self._lookup_field_value = None
        super().__init__()

    @property
    def id(self):
        result = f'{self.service}_{self._app}_{self._view_set}'
        result = result if self._lookup_field_value is None else f'{result}_{self._lookup_field_value}'
        result = result if self._action is None else f'{result}_{self._action}'
        return result

    @property
    def service(self):
        return self._service

    @property
    def path(self):
        result = f'/{self._app}/{self._view_set}'
        result = result if self._lookup_field_value is None else f'{result}/{self._lookup_field_value}'
        result = result if self._action is None else f'{result}/{self._action}'
        return result

    @property
    def url(self):
        result = f'https://{self.service}.expressmoney.com/{self._app}/{self._view_set}'
        result = result if self._lookup_field_value is None else f'{result}/{self._lookup_field_value}'
        result = result if self._action is None else f'{result}/{self._action}'
        return result

    @property
    def lookup_field_value(self):
        return self._lookup_field_value

    @lookup_field_value.setter
    def lookup_field_value(self, value):
        self._lookup_field_value = value
