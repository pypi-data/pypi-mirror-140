from django.core.validators import RegexValidator

from expressmoney.api import *

__all__ = ('UploadFilePoint', 'UserFilePoint',)
SERVICE_NAME = 'storage'


class UserFileReadContract(Contract):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z_]*$', 'Only alphanumeric characters are allowed.')

    id = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=64, validators=(alphanumeric,))
    file = serializers.URLField()
    public_url = serializers.URLField(allow_null=True)


storage_storage_user_file = ServicePoint(SERVICE_NAME, 'storage', 'user_file')
storage_storage_upload_file = ServicePoint(SERVICE_NAME, 'storage', 'user_file/')


class UserFilePoint(ListMixin, ContractPoint):
    _read_contract = UserFileReadContract
    _service_point = storage_storage_user_file
    _app = 'storage'
    _point = 'user_file'


class UploadFilePoint(ContractPoint):
    _service_point = storage_storage_upload_file
    _read_contract = None
