from typing import OrderedDict


__all__ = ('FilterMixin',)


class FilterError(Exception):
    pass


class FilterAttrNotSet(FilterError):
    pass


class FilterMixin:

    def filter(self, **kwargs) -> tuple:
        if not kwargs:
            raise FilterAttrNotSet('Set filter attr. Example: status="NEW"')
        key, find_value = next(iter(kwargs.items()))
        find_value = find_value if isinstance(find_value, (list, tuple)) else (find_value,)
        result = [item for item in self.list() if item.get(key) in find_value]
        return tuple(result)

    def first(self) -> OrderedDict:
        result = self.list()
        return result[0] if len(result) > 0 else None

    def last(self) -> OrderedDict:
        result = self.list()
        return result[-1] if len(result) > 0 else None

    def filter_first(self, **kwargs) -> OrderedDict:
        result = self.filter(**kwargs)
        return result[0] if len(result) > 0 else None

    def filter_last(self, **kwargs) -> OrderedDict:
        result = self.filter(**kwargs)
        return result[-1] if len(result) > 0 else None
