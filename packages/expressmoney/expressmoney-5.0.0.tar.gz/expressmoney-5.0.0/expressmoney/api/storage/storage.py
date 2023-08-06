__all__ = ('UploadFilePoint', 'UserFilePoint',)

from django.core.validators import RegexValidator

from expressmoney.api import *

SERVICE_NAME = 'storage'


class UserFileReadContract(Contract):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z_]*$', 'Only alphanumeric characters are allowed.')

    id = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=64, validators=(alphanumeric,))
    file = serializers.URLField()
    public_url = serializers.URLField(allow_null=True)


storage_storage_user_file = ID(SERVICE_NAME, 'storage', 'user_file')
storage_storage_upload_file = ID(SERVICE_NAME, 'storage', 'upload_file/')


class UserFilePoint(ListPointMixin, ContractPoint):
    _read_contract = UserFileReadContract
    _point_id = storage_storage_user_file
    _app = 'storage'
    _point = 'user_file'


class UploadFilePoint(UploadFilePointMixin, ContractPoint):
    _point_id = storage_storage_upload_file
    _read_contract = None
