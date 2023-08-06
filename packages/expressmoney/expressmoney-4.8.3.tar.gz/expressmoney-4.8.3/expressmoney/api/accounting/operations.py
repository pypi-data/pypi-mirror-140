__all__ = ('LoansIssuePoint', 'LoanPaymentBodyPoint', 'LoansInterestsChargePoint', 'LoansPaymentInterestsPoint')

from expressmoney.api import *
from expressmoney.api.accounting.balances import *

SERVICE_NAME = 'accounting'


class LoansIssueCreateContract(Contract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0, min_value=1, max_value=1000000000)
    department = serializers.IntegerField(min_value=1)
    analytical = serializers.IntegerField(min_value=1)


class LoanPaymentBodyCreateContract(LoansIssueCreateContract):
    pass


class LoansInterestsChargeCreateContract(LoansIssueCreateContract):
    pass


class LoansPaymentInterestsCreateContract(LoansIssueCreateContract):
    pass


accounting_operations_loans_issue = ServicePoint(SERVICE_NAME, 'operations', 'loans_issue')
accounting_operations_loans_payment_body = ServicePoint(SERVICE_NAME, 'operations', 'loans-payment-body')
accounting_operations_loans_interests_charge = ServicePoint(SERVICE_NAME, 'operations', 'loans_interests_charge')
accounting_operations_loans_payment_interests = ServicePoint(SERVICE_NAME, 'operations', 'loans_payment_interests')


class LoansIssuePoint(CreatePointMixin, ContractPoint):
    """Issue loan body (Dt48801 Kt47422)"""
    _service_point = accounting_operations_loans_issue
    _create_contract = LoansIssueCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(A48801BalanceAnalyticalPoint(self._user, loan))
        return related_points


class LoanPaymentBodyPoint(CreatePointMixin, ContractPoint):
    """Payment loan body (Dt47423 Kt48801)"""
    _service_point = accounting_operations_loans_payment_body
    _create_contract = LoanPaymentBodyCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(A48801BalanceAnalyticalPoint(self._user, loan))
        return related_points


class LoansInterestsChargePoint(CreatePointMixin, ContractPoint):
    """Charge loan interests (Dt48802 Kt71001)"""
    _service_point = accounting_operations_loans_interests_charge
    _create_contract = LoansInterestsChargeCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(A48802BalanceAnalyticalPoint(self._user, loan))
        return related_points


class LoansPaymentInterestsPoint(CreatePointMixin, ContractPoint):
    """Payment loan interests (Dt47423 Kt48809)"""
    _service_point = accounting_operations_loans_payment_interests
    _create_contract = LoansPaymentInterestsCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(P48809BalanceAnalyticalPoint(self._user, loan))
        return related_points


"""
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)

from expressmoney.api.accounting import LoanPaymentBodyPoint
point = p = LoanPaymentBodyPoint(user)
p.create({
    "amount": 500,
    "department": 1,
    "analytical": 44
})
response = p.get_response()
"""
