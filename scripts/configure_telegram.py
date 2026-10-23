import json
import os
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def call_api(token: str, method: str, payload: dict) -> dict:
    body = urlencode({"menu_button": json.dumps(payload)}).encode()
    request = Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram API request failed"))
    return result


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    app_url = os.environ.get("TELEGRAM_APP_URL")
    if not token or not app_url:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_APP_URL first")
    call_api(token, "setChatMenuButton", {
        "type": "web_app",
        "text": os.environ.get("TELEGRAM_MENU_TEXT", "Открыть приложение"),
        "web_app": {"url": app_url},
    })
    print(f"Telegram menu button configured for {app_url}")


if __name__ == "__main__":
    main()
