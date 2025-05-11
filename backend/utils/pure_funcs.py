import secrets
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import uuid


def get_uuid():
    return str(uuid.uuid4())


def get_now():
    return datetime.now(timezone.utc)


def gen_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def round_decimal(value, decimal_places: int = 2) -> float:

    decimal_value = Decimal(value)

    quantize_target = Decimal('1.' + '0' * decimal_places)

    rounded_value = decimal_value.quantize(
        quantize_target, rounding=ROUND_HALF_UP)

    return float(rounded_value)
