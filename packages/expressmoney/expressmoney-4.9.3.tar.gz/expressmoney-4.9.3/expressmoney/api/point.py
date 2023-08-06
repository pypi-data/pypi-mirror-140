"""
Endpoints handlers
"""

__all__ = ('RequestError', 'ClientError', 'ServerError', 'NotFound404',
           'Point', 'ObjectPoint', 'ContractPoint', 'ContractObjectPoint',
           'ListPointMixin', 'RetrievePointMixin', 'CreatePointMixin', 'UpdatePointMixin', 'UploadFilePointMixin',
           'ActionPointMixin',
           )

from typing import OrderedDict, Union

from django.contrib.auth import get_user_model

from expressmoney.api.cache import CacheMixin, CacheObjectMixin
from expressmoney.api.filter import FilterMixin
from expressmoney.api.utils import log
from expressmoney.django.utils import DjangoRequest
from expressmoney.utils import HttpStatus

User = get_user_model()


class PointError(Exception):
    pass


class RequestError(PointError):
    pass


class ServerError(RequestError):
    pass


class ClientError(RequestError):
    pass


class NotFound404(ClientError):
    pass


class LookupFieldValueNone(PointError):
    pass


class SortByNotSet(PointError):
    pass


class FilterAttrNotSet(PointError):
    pass


class ContractNotSet(PointError):
    pass


class Point:
    """Base endpoint handler"""
    _point_id = None

    @log
    def __init__(self, user: User):
        self._user = user
        self._cache = None
        self._response = None
        self._service = DjangoRequest(
            service=self._point_id.service,
            path=self._path,
            user=user
        )

    def get_response(self):
        return self._response

    @property
    def _path(self):
        path = self._point_id.path
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
                if HttpStatus.is_not_found(response.status_code):
                    self._cache = HttpStatus.HTTP_404_NOT_FOUND
                    raise NotFound404(self._point_id.url)
                else:
                    raise ClientError(f'{response.status_code}:{self._point_id.url}:{response.json()}')
            else:
                raise ServerError(f'{response.status_code}:{self._point_id.url}:{response.text}')


class ObjectPoint(Point):
    """For one object endpoints"""

    def __init__(self, user: User, lookup_field_value: Union[None, str, int] = None):
        if lookup_field_value is None:
            raise LookupFieldValueNone('lookup_field_value not filled')
        self._lookup_field_value = lookup_field_value
        self._point_id.lookup_field_value = lookup_field_value
        super().__init__(user)

    def _put(self, payload: dict):
        self._response = self._service.put(payload=payload)
        self._handle_error(self._response)

    # @property
    # def _path(self) -> str:
    #     path = f'/{self._endpoint.path}/{self._lookup_field_value}'
    #     return path


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
        if HttpStatus.is_not_found(data):
            raise NotFound404
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


class ListPointMixin:
    """For type ContractPoint"""

    def list(self) -> tuple:
        if self._read_contract is None:
            raise ContractNotSet(f'Set attr read_contract')
        return self._sorted_data


class RetrievePointMixin:
    """For type ContractObjectPoint"""

    def retrieve(self) -> OrderedDict:
        if self._read_contract is None:
            raise ContractNotSet(f'Set attr read_contract')
        return self._get_validated_data()


class CreatePointMixin:
    """For type ContractPoint"""

    def create(self, payload: dict):
        if self._create_contract is None:
            raise ContractNotSet(f'Set attr create_contract')

        contract = self._get_contract(data=payload, is_read=False)
        self._post(contract.data)


class UpdatePointMixin:
    """For type ContractObjectPoint"""

    def update(self, payload: dict):
        if self._update_contract is None:
            raise ContractNotSet(f'Set attr update_contract')

        contract = self._get_contract(data=payload, is_read=False)
        self._put(contract.validated_data)


class UploadFilePointMixin:
    """For any type Point"""

    def upload_file(self, file, filename: str, file_type: int):
        self._post_file(file, filename, file_type)


class ActionPointMixin:
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


from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)
from expressmoney.api.accounting.balances import A48801BalanceAnalyticalPoint
b = A48801BalanceAnalyticalPoint(user, 44)
b.retrieve()
"""
