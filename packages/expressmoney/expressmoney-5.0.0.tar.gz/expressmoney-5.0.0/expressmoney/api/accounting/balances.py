__all__ = ('A48801BalanceAnalyticalPoint', 'A48802BalanceAnalyticalPoint', 'P48809BalanceAnalyticalPoint')

from expressmoney.api import *

SERVICE_NAME = 'accounting'


class A48801BalanceAnalyticalReadContract(Contract):
    id = serializers.IntegerField(min_value=1)
    updated = serializers.DateTimeField()
    balance = serializers.DecimalField(max_digits=16, decimal_places=0)


class A48802BalanceAnalyticalReadContract(A48801BalanceAnalyticalReadContract):
    pass


class P48809BalanceAnalyticalReadContract(A48801BalanceAnalyticalReadContract):
    pass


accounting_balances_a48801_balance_analytical = ID(SERVICE_NAME, 'balances', 'a48801_balance_analytical')
accounting_balances_a48802_balance_analytical = ID(SERVICE_NAME, 'balances', 'a48802_balance_analytical')
accounting_balances_p48809_balance_analytical = ID(SERVICE_NAME, 'balances', 'p48809_balance_analytical')


class A48801BalanceAnalyticalPoint(RetrievePointMixin, ContractObjectPoint):
    """Loan body balance"""
    _point_id = accounting_balances_a48801_balance_analytical
    _read_contract = A48801BalanceAnalyticalReadContract


class A48802BalanceAnalyticalPoint(RetrievePointMixin, ContractObjectPoint):
    """Total loan interests charged"""
    _point_id = accounting_balances_a48802_balance_analytical
    _read_contract = A48802BalanceAnalyticalReadContract


class P48809BalanceAnalyticalPoint(RetrievePointMixin, ContractObjectPoint):
    """Interests paid"""
    _point_id = accounting_balances_p48809_balance_analytical
    _read_contract = P48809BalanceAnalyticalReadContract


"""
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)

from expressmoney.api.accounting import A48801BalanceAnalyticalPoint
point = A48801BalanceAnalyticalPoint(user, 44)
result = point.retrieve()

"""
