__all__ = ('BankCardPaymentPoint',)

from expressmoney.api import *

SERVICE = 'payments'


class BankCardPaymentCreateContract(Contract):
    LOAN_BODY = 'LOAN_BODY'
    LOAN_INTERESTS = 'LOAN_INTERESTS'
    LOAN_ISSUE = 'LOAN_ISSUE'

    TYPE_CHOICES = {
        (LOAN_BODY, 'Loan body'),
        (LOAN_INTERESTS, 'Loan interests'),
        (LOAN_ISSUE, 'Loan issue'),
    }

    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    amount = serializers.DecimalField(max_digits=16, decimal_places=0, min_value=1, max_value=100000)
    analytical = serializers.IntegerField(min_value=1)
    department = serializers.IntegerField(min_value=1)
    bank_card = serializers.IntegerField(min_value=1)


class BankCardPaymentListContract(BankCardPaymentCreateContract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()


payments_payments_payment_bank_card = ID(SERVICE, 'payments', 'bank_card_payment')


class BankCardPaymentPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = payments_payments_payment_bank_card
    _create_contract = BankCardPaymentCreateContract
    _read_contract = BankCardPaymentListContract


"""
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)

point = LoanPaymentBodyPoint(user)
point.create({"amount": 100, "department": 13, "analytical": 44})

from loans.models import Loan
loan = Loan.objects.get(id=44)
print(loan.body_balance)

from expressmoney.api.payments import BankCardPaymentPoint
point = BankCardPaymentPoint(user).create({"type": "LOAN_INTERESTS", "amount": "10", "analytical": 44, "department": 13, "bank_card": 1})
"""