import json
from urllib.request import Request, urlopen


def send_message(bot_token: str, chat_id: int, text: str) -> None:
    if not bot_token:
        return
    body = json.dumps({"chat_id": chat_id, "text": text}).encode()
    request = Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        if response.status >= 400:
            raise RuntimeError(f"Telegram API returned HTTP {response.status}")
