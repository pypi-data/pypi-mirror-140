from dataclasses import dataclass
from typing import OrderedDict

from django.contrib.auth import get_user_model

from expressmoney.api.cache import CacheMixin, CacheObjectMixin
from expressmoney.api.filters import FilterMixin
from expressmoney.api.utils import log
from expressmoney.django.utils import DjangoRequest
from expressmoney.utils import HttpStatus

__all__ = ('ClientError', 'ServerError',
           'Point', 'ObjectPoint', 'ContractPoint', 'ContractObjectPoint', 'ServicePoint',
           'ListMixin', 'RetrieveMixin', 'CreateMixin', 'UpdateMixin', 'UploadMixin', 'ActionMixin',
           )

User = get_user_model()


class PointError(Exception):
    pass


class ClientError(PointError):
    pass


class ServerError(PointError):
    pass


class LookupFieldValueNone(PointError):
    pass


class SortByNotSet(PointError):
    pass


class FilterAttrNotSet(PointError):
    pass


class CreateContractNotSet(PointError):
    pass


class UpdateContractNotSet(PointError):
    pass


@dataclass
class ServicePoint:
    """Microservice endpoint"""
    service: str = None
    app: str = None
    view_set: str = None

    @property
    def path(self):
        return f'/{self.app}/{self.view_set}'

    @property
    def url(self):
        return f'https://{self.service}.expressmoney.com/{self.app}/{self.view_set}'

    @property
    def id(self):
        return f'{self.service}_{self.app}_{self.view_set}'


class Point:
    """REST API Endpoint"""
    _service_point = None
    _app = None
    _point = None

    @log
    def __init__(self, user: User):
        self._cache = None
        self._response = None
        self._service = DjangoRequest(
            service=self._service_point.service,
            path=self._path,
            user=user
        )

    def get_response(self):
        return self._response

    @property
    def _path(self):
        path = self._service_point.path
        return path

    def _post(self, payload: dict):
        self._response = self._service.post(payload=payload)
        self._handle_error(self._response)

    @log
    def _get(self) -> dict:
        self._response = self._service.get()
        self._handle_error(self._response)
        data = self._response.json()
        return data

    def _post_file(self, file, file_name, type_):
        self._response = self._service.post_file(file=file, file_name=file_name, type_=type_)
        self._handle_error(self._response)

    def _handle_error(self, response):
        if not HttpStatus.is_success(response.status_code):
            if HttpStatus.is_client_error(response.status_code):
                raise ClientError(f'{response.status_code}:{self._service_point}:{response.json()}')
            raise ServerError(f'{response.status_code}:{self._service_point}:{response.text}')


class ObjectPoint(Point):
    """For one object endpoints"""
    _lookup_field_value = None

    def __init__(self, user: User, lookup_field_value: str = None):
        if lookup_field_value is None:
            raise LookupFieldValueNone('lookup_field_value not filled')
        self._lookup_field_value = lookup_field_value
        super().__init__(user)

    def _put(self, payload: dict):
        self._response = self._service.put(payload=payload)
        self._handle_error(self._response)

    @property
    def _path(self) -> str:
        path = f'/{self._service_point.path}/{self._lookup_field_value}'
        return path


class ContractPoint(FilterMixin, CacheMixin, Point):
    """Endpoints with validated data by contract"""
    _read_contract = None
    _create_contract = None
    _sort_by = 'id'

    @property
    def _sorted_data(self) -> tuple:
        if self._sort_by is None:
            raise SortByNotSet('Set key for sort or False')
        validated_data = self._get_validated_data()
        sorted_data = sorted(validated_data, key=lambda obj: obj[self._sort_by]) if self._sort_by else validated_data
        return tuple(sorted_data)

    def _get_validated_data(self):
        data = self._handle_pagination(self._get())
        contract = self._get_contract(data, True)
        validated_data = contract.validated_data
        if self._cache is None:
            self._cache = validated_data
        return validated_data

    def _get_contract(self, data, is_read: bool):
        contract_class = self._get_contract_class(is_read)
        contract = contract_class(data=data, many=True if is_read else False)
        contract.is_valid(raise_exception=True)
        return contract

    def _get_contract_class(self, is_read: bool):
        return self._read_contract if is_read else self._create_contract

    @staticmethod
    def _handle_pagination(data):
        """Get current page and link on next page"""
        if isinstance(data, list) or None in (data.get('count'), data.get('results')):
            return data
        pagination = {
            'previous': data.get('previous'),
            'next': data.get('next'),
            'count': data.get('count'),
        }
        data = data.get('results')
        data = [dict(**entity, pagination=pagination) for entity in data]
        return data


class ContractObjectPoint(CacheObjectMixin, ObjectPoint):
    """Endpoints for one object with validated data by contract"""
    _read_contract = None
    _update_contract = None

    def _get_validated_data(self):
        data = self._get()
        contract = self._get_contract(data, True)
        validated_data = contract.validated_data
        if self._cache is None:
            self._cache = validated_data
        return validated_data

    def _get_contract(self, data, is_read: bool):
        contract_class = self._get_contract_class(is_read)
        contract = contract_class(data=data, many=False)
        contract.is_valid(raise_exception=True)
        return contract

    def _get_contract_class(self, is_read: bool):
        return self._read_contract if is_read else self._update_contract


class ListMixin:
    """For type ContractPoint"""

    def list(self) -> tuple:
        return self._sorted_data


class RetrieveMixin:
    """For type ContractObjectPoint"""

    def retrieve(self) -> OrderedDict:
        return self._get_validated_data()


class CreateMixin:
    """For type ContractPoint"""

    def create(self, payload: dict):
        if self._create_contract is None:
            raise CreateContractNotSet(f'Set attr create_contract')

        contract = self._get_contract(data=payload, is_read=False)
        self._post(contract.data)


class UpdateMixin:
    """For type ContractObjectPoint"""

    def update(self, payload: dict):
        if self._update_contract is None:
            raise UpdateContractNotSet(f'Set attr update_contract')

        contract = self._get_contract(data=payload, is_read=False)
        self._put(contract.validated_data)


class UploadMixin:
    """For any type Point"""

    def upload_file(self, file, filename: str, file_type: int):
        self._post_file(file, filename, file_type)


class ActionMixin:
    """For any type Point"""

    def action(self):
        self._get()


"""
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)
from loans.api import  OrderApi
order_api = OrderApi(user)

from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)
from loans.api import  OrderApi
order_api = OrderApi(user)
order_api.all()

from orders.models import Order
from loans.utils import RussianLoanContract
from expressmoney.api.storage import UploadFileAPI
order = Order.objects.get(pk=1)
contract = RussianLoanContract(order, True).create()
filename = f'loan_contract_demo_{order.id}.pdf'
upload_file_api = UploadFileAPI(order.user_id)
upload_file_api.upload_file(contract, filename, 3)


from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)
from expressmoney.api.loans import OrderListPoint
orders = OrderListPoint(user)
r = orders.list()

from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)
from expressmoney.api.cache import FlushCache
FlushCache(user).flush_cache()
"""