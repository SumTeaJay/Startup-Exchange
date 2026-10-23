import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from app.security import validate_telegram_init_data


def make_init_data(token: str, user: dict, auth_date: int | None = None) -> str:
    values = {
        "auth_date": str(auth_date or int(time.time())),
        "query_id": "AA-test-query",
        "user": json.dumps(user, separators=(",", ":")),
    }
    check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_valid_telegram_init_data_is_accepted():
    user = {"id": 123456789, "first_name": "Ada", "username": "ada"}
    init_data = make_init_data("bot-token", user)

    assert validate_telegram_init_data(init_data, "bot-token")["id"] == 123456789


def test_tampered_telegram_init_data_is_rejected():
    init_data = make_init_data("bot-token", {"id": 123456789})
    tampered = init_data.replace("123456789", "987654321")

    with pytest.raises(ValueError, match="invalid"):
        validate_telegram_init_data(tampered, "bot-token")


def test_expired_telegram_init_data_is_rejected():
    init_data = make_init_data("bot-token", {"id": 123456789}, int(time.time()) - 90000)

    with pytest.raises(ValueError, match="expired"):
        validate_telegram_init_data(init_data, "bot-token", max_age_seconds=86400)
