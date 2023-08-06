__all__ = ('LoanPoint', 'LoanPaginationNonePoint', 'PayPoint',)

from typing import OrderedDict, Union

from expressmoney.api import *

SERVICE_NAME = 'loans'


class LoanCreateContract(Contract):
    sign = serializers.IntegerField()


class LoanReadContract(LoanCreateContract):
    OPEN = "OPEN"
    OVERDUE = "OVERDUE"
    STOP_INTEREST = "STOP_INTEREST"
    DEFAULT = "DEFAULT"
    CLOSED = "CLOSED"
    STATUS_CHOICES = {
        (OPEN, gettext_lazy("Open loan")),
        (OVERDUE, gettext_lazy("Overdue loan")),
        (STOP_INTEREST, gettext_lazy("Stop interest loan")),
        (DEFAULT, gettext_lazy("Default loan")),
        (CLOSED, gettext_lazy("Closed loan")),
    }
    OPEN_STATUSES = (OPEN, OVERDUE, STOP_INTEREST, DEFAULT)

    pagination = PaginationContract()
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()

    amount = serializers.DecimalField(max_digits=7, decimal_places=0, allow_null=True)
    period = serializers.IntegerField()
    expiry_date = serializers.DateField()
    expiry_period = serializers.IntegerField()

    interests_charged_date = serializers.DateField(allow_null=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES)

    body_balance = serializers.DecimalField(max_digits=7, decimal_places=0, allow_null=True)
    body_paid = serializers.DecimalField(max_digits=7, decimal_places=0, allow_null=True)
    interests_total = serializers.DecimalField(max_digits=7, decimal_places=0, allow_null=True)
    interests_paid = serializers.DecimalField(max_digits=7, decimal_places=0, allow_null=True)
    interests_balance = serializers.DecimalField(max_digits=7, decimal_places=0)

    document = serializers.CharField(max_length=256, allow_blank=True)
    comment = serializers.CharField(max_length=2048, allow_blank=True)


class LoanPaginationNoneReadContract(LoanReadContract):
    pagination = None


class PayUpdateContract(Contract):
    bank_card_id = serializers.IntegerField()


loans_loans_loan = ID(SERVICE_NAME, 'loans', 'loan')
loans_loans_loan_pagination_none = ID(SERVICE_NAME, 'loans', 'loan', 'pagination_none')
loans_loans_pay = ID(SERVICE_NAME, 'loans', 'pay')


class LoanPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = loans_loans_loan
    _read_contract = LoanReadContract
    _create_contract = LoanCreateContract

    def open_loans(self) -> tuple:
        return self.filter(status=self._read_contract.OPEN_STATUSES)

    def open_loans_last(self) -> Union[None, OrderedDict]:
        objects = self.open_loans()
        return objects[-1] if len(objects) > 0 else None

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        related_points.append(LoanPaginationNonePoint(self._user))
        return related_points


class LoanPaginationNonePoint(ListPointMixin, ContractPoint):
    _point_id = loans_loans_loan_pagination_none
    _read_contract = LoanPaginationNoneReadContract


class PayPoint(UpdatePointMixin, ContractObjectPoint):
    _point_id = loans_loans_pay
    _update_contract = PayUpdateContract


"""
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)

from loans.models import Loan
loan = Loan.objects.get(id=47)
print(loan.body_balance)

"""
