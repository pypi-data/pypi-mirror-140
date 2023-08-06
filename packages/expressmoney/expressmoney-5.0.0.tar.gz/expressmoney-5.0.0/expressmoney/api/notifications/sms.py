__all__ = ('SmsPoint',)

from expressmoney.api import *


SERVICE_NAME = 'notifications'


class SmsCreateContract(Contract):
    message = serializers.CharField(min_length=1, max_length=60)


notifications_sms_sms = ID(SERVICE_NAME, 'sms', 'sms')


class SmsPoint(CreatePointMixin, ContractPoint):
    _point_id = notifications_sms_sms
    _create_contract = SmsCreateContract
