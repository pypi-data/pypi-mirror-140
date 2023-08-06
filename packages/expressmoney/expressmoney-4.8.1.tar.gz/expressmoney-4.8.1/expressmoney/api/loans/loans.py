from expressmoney.api import *

__all__ = ('LoanPoint', 'PayPoint', )

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


class PayUpdateContract(Contract):
    bank_card_id = serializers.IntegerField()


loans_loans_loan = ServicePoint(SERVICE_NAME, 'loans', 'loan')
loans_loans_pay = ServicePoint(SERVICE_NAME, 'loans', 'pay')


class LoanPoint(ListMixin, CreateMixin, ContractPoint):
    _service_point = loans_loans_loan
    _read_contract = LoanReadContract
    _create_contract = LoanCreateContract

    def open_loans(self):
        return self.filter(status=self._read_contract.OPEN_STATUSES)

    def open_loans_last(self):
        objects = self.open_loans()
        return objects[-1] if len(objects) > 0 else None


class PayPoint(UpdateMixin, ContractObjectPoint):
    _service_point = loans_loans_pay
    _update_contract = PayUpdateContract
