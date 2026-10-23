import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

import jwt

from app.config import get_settings


def hash_password(password: str) -> str:
    salt = hashlib.sha256(password.encode()).hexdigest()[:32]
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt, expected = encoded.split("$", 1)
    except ValueError:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expires}, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token subject is missing")
    return user_id


def validate_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> dict:
    if not bot_token:
        raise ValueError("Telegram bot token is not configured")
    values = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = values.pop("hash", None)
    if not received_hash:
        raise ValueError("Telegram hash is missing")
    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(values.items())
    )
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValueError("Telegram signature is invalid")
    try:
        auth_date = int(values["auth_date"])
        user = json.loads(values["user"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Telegram init data is malformed") from exc
    if time.time() - auth_date > max_age_seconds:
        raise ValueError("Telegram init data has expired")
    if time.time() < auth_date - 60:
        raise ValueError("Telegram auth date is invalid")
    if not isinstance(user, dict) or not user.get("id"):
        raise ValueError("Telegram user is missing")
    return user
