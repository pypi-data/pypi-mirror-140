__all__ = ('BankCardPoint',)

from expressmoney.api import *


SERVICE_NAME = 'payments'


class BankCardContract(Contract):
    M01 = "01"
    M02 = "02"
    M03 = "03"
    M04 = "04"
    M05 = "05"
    M06 = "06"
    M07 = "07"
    M08 = "08"
    M09 = "09"
    M10 = "10"
    M11 = "11"
    M12 = "12"

    MONTH_CHOICES = (
        (M01, '01'),
        (M02, '02'),
        (M03, '03'),
        (M04, '04'),
        (M05, '05'),
        (M06, '06'),
        (M07, '07'),
        (M08, '08'),
        (M09, '09'),
        (M10, '10'),
        (M11, '11'),
        (M12, '12'),
    )

    Y2020 = "2020"
    Y2021 = "2021"
    Y2022 = "2022"
    Y2023 = "2023"
    Y2024 = "2024"
    Y2025 = "2025"
    Y2026 = "2026"
    Y2027 = "2027"
    Y2028 = "2028"
    Y2029 = "2029"
    Y2030 = "2030"

    YEAR_CHOICES = (
        (Y2020, "2020"),
        (Y2021, "2021"),
        (Y2022, "2022"),
        (Y2023, "2023"),
        (Y2024, "2024"),
        (Y2025, "2025"),
        (Y2026, "2026"),
        (Y2027, "2027"),
        (Y2028, "2028"),
        (Y2029, "2029"),
        (Y2030, "2030"),
    )

    PAYPAL = "PAYPAL"
    CLOUDPAYMENTS = "CLOUDPAYMENTS"
    GATEWAY_CHOICES = (
        (PAYPAL, "PayPal"),
        (CLOUDPAYMENTS, "CloudPayments")
    )
    pagination = PaginationContract()
    id = serializers.IntegerField(min_value=1)
    is_active = serializers.BooleanField(default=True)
    bin = serializers.CharField(max_length=6)
    number = serializers.CharField(max_length=4)
    expiry_month = serializers.ChoiceField(choices=MONTH_CHOICES)
    expiry_year = serializers.ChoiceField(choices=YEAR_CHOICES)
    ip = serializers.IPAddressField(allow_blank=True)
    cryptogram = serializers.CharField(max_length=1024, allow_blank=True)
    redirect_url = serializers.URLField(max_length=512, allow_blank=True)
    gateway = serializers.ChoiceField(choices=GATEWAY_CHOICES)


payments_bank_cards_bank_card = ID(SERVICE_NAME, 'bank_cards', 'bank_card')


class BankCardPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = payments_bank_cards_bank_card
    _read_contract = BankCardContract


"""
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=1)
"""