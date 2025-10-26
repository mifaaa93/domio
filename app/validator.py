# app/validator.py
import hmac, hashlib, json, time
from urllib.parse import parse_qsl
from typing import Optional, TypedDict
from fastapi import Header, HTTPException
from config import BOT_TOKEN


class MiniAppAuth(TypedDict, total=False):
    user: dict
    query_id: str
    auth_date: int

def _verify_init_data(init_data: str, *, max_age: int = 24*60*60) -> Optional[MiniAppAuth]:
    try:
        # 1) Разбор без потерь
        data = dict(parse_qsl(init_data, strict_parsing=True))

        # 2) hash берём, signature игнорируем (не участвует в подписи!)
        received_hash = data.pop("hash", "")
        if not received_hash:
            return None

        # 3) Формируем data_check_string
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items(), key=lambda item: item[0]))

        # 4) Секрет = HMAC_SHA256("WebAppData", BOT_TOKEN)
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()

        # 5) Итоговый хеш
        computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed, received_hash):
            return None

        # 6) Anti-replay
        try:
            auth_date = int(data.get("auth_date", "0"))
        except ValueError:
            return None

        now = int(time.time())
        if max_age > 0 and abs(now - auth_date) > max_age:
            return None

        # 7) Полезные поля
        auth: MiniAppAuth = {"auth_date": auth_date}
        if "user" in data:
            auth["user"] = json.loads(data["user"])
        if "query_id" in data:
            auth["query_id"] = data["query_id"]
        return auth

    except Exception as e:
        return None

async def valid_user_from_header(
    init_data: str | None = Header(alias="X-Telegram-Init-Data"),
) -> MiniAppAuth:
    
    if not init_data:
        raise HTTPException(status_code=400, detail="initData is required")
    auth = _verify_init_data(init_data)
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid initData")
    return auth
