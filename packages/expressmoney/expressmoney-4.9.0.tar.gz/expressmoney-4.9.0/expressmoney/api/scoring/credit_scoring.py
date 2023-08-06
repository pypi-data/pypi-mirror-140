__all__ = ('OrderPoint',)

from expressmoney.api import *


SERVICE_NAME = 'scoring'


class OrderCreateContract(Contract):
    order_id = serializers.IntegerField(min_value=1)


class OrderReadContract(Contract):
    created = serializers.DateTimeField()
    score = serializers.DecimalField(max_digits=3, decimal_places=2)


scoring_credit_scoring_order = ServicePoint(SERVICE_NAME, 'credit_scoring', 'order')


class OrderPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _service_point = scoring_credit_scoring_order
    _read_contract = OrderReadContract
    _create_contract = OrderCreateContract


"""


"""