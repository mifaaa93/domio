# payu/payu_client.py
from __future__ import annotations
import json
import time
import hmac
import hashlib
import uuid
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional, Iterable

import httpx
from httpx import HTTPError

from config import (
    PAYU_POS_ID,
    PAYU_CLIENT_ID,
    PAYU_CLIENT_SECRET,
    PAYU_SECOND_KEY,
    PAYU_SANDBOX,

)


# ========= Errors =========
class PayUError(Exception):
    """Базовая ошибка PayU с полезным контекстом (HTTP, headers, text/json)."""
    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        payload: Any = None,
        headers: Optional[dict] = None,
        text: Optional[str] = None,
    ):
        super().__init__(message)
        self.status = status
        self.payload = payload
        self.headers = headers or {}
        self.text = text


# ========= Config =========

@dataclass
class PayUConfig:
    pos_id: str
    client_id: str
    client_secret: str
    second_key: str
    sandbox: bool = True
    # таймауты/повторы:
    request_timeout_s: float = 30.0
    oauth_timeout_s: float = 20.0
    max_retries: int = 2            # кроме 401 (для него отдельный forced refresh)
    retry_backoff_s: float = 0.4    # экспоненциальная задержка: 0.4, 0.8, ...
    # кастомные заголовки (если когда-нибудь появятся требования):
    extra_headers: Dict[str, str] | None = None

    @property
    def base_url(self) -> str:
        return "https://secure.snd.payu.com" if self.sandbox else "https://secure.payu.com"


# ========= Client =========

class PayUClient:
    """
    Асинхронный клиент PayU (Poland) с:
    - кешированием OAuth-токена (access_token, expires_in)
    - безопасным обновлением токена (asyncio.Lock)
    - повторными попытками при сетевых/временных ошибках (5xx/429) и единичным ретраем при 401
    - единым httpx.AsyncClient на весь инстанс
    - расширяемыми полями заказа (payMethods, products, ext_fields)
    """

    def __init__(self, cfg: PayUConfig) -> None:
        self.cfg = cfg
        self._token: Optional[str] = None
        self._token_exp: float = 0.0
        self._lock = asyncio.Lock()
        self._http: Optional[httpx.AsyncClient] = None
        self._default_headers = {
    "User-Agent": "DomioPayUClient/1.0 (+support@your.app)",
}

    # ----- lifecycle -----
    def _ensure_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(
                timeout=self.cfg.request_timeout_s,
                headers=self._default_headers,)
        return self._http

    async def aclose(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    async def __aenter__(self) -> "PayUClient":
        self._ensure_http()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    # ========= OAuth =========

    async def _ensure_token(self, force_refresh: bool = False) -> str:
        now = time.time()
        if not force_refresh and self._token and now < self._token_exp - 30:
            return self._token

        async with self._lock:
            # повторная проверка под локом
            now = time.time()
            if not force_refresh and self._token and now < self._token_exp - 30:
                return self._token

            http = httpx.AsyncClient(timeout=self.cfg.oauth_timeout_s)
            try:
                url = f"{self.cfg.base_url}/pl/standard/user/oauth/authorize"
                data = {
                    "grant_type": "client_credentials",
                    "client_id": self.cfg.client_id,
                    "client_secret": self.cfg.client_secret,
                }
                r = await http.post(url, data=data)
                r.raise_for_status()
                j = r.json()
                self._token = j["access_token"]
                self._token_exp = now + int(j.get("expires_in", 3600))
                return self._token
            except HTTPError as e:
                raise PayUError("OAuth token request failed", status=getattr(e.response, "status_code", None)) from e
            finally:
                await http.aclose()

    def _auth_headers(self, token: str) -> Dict[str, str]:
        base = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }
        if self.cfg.extra_headers:
            base.update(self.cfg.extra_headers)
        return base

    # ========= Low-level HTTP with retries =========

    async def _retry_wait(self, attempt: int) -> None:
        # экспоненциальная задержка
        await asyncio.sleep(self.cfg.retry_backoff_s * (2 ** (attempt - 1)))

    def _should_retry(self, status: Optional[int]) -> bool:
        return (status is None) or (500 <= status <= 599) or (status == 429)

    async def _request_json(
        self,
        method: str,
        url: str,
        *,
        body: Optional[dict] = None,
        retry_on_401: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        token = await self._ensure_token()
        headers = self._auth_headers(token)
        if extra_headers:
            headers.update(extra_headers)
        content = json.dumps(body) if body is not None else None

        http = self._ensure_http()

        # Базовые повторы (429/5xx/сеть)
        last_exc: Optional[Exception] = None
        for attempt in range(0, self.cfg.max_retries + 1):
            try:
                r = await http.request(method, url, headers=headers, content=content)
                if r.status_code == 401 and retry_on_401:
                    # форс-обновляем токен и пробуем ещё раз (один цикл)
                    token = await self._ensure_token(force_refresh=True)
                    headers = self._auth_headers(token)
                    if extra_headers:
                        headers.update(extra_headers)
                    r = await http.request(method, url, headers=headers, content=content)
                if 300 <= r.status_code < 400:
                    data = r.json() if r.text else {}
                    loc = r.headers.get("location")
                    # подложим redirectUri, если вдруг нет в JSON
                    if loc and "redirectUri" not in data:
                        data["redirectUri"] = loc
                    return data
                r.raise_for_status()
                return r.json() if r.text else {}
            except HTTPError as e:
                status = getattr(e.response, "status_code", None)
                if attempt < self.cfg.max_retries and self._should_retry(status):
                    await self._retry_wait(attempt + 1)
                    last_exc = e
                    continue
                detail = None
                text = None
                try:
                    detail = e.response.json()
                except Exception:
                    text = getattr(e.response, "text", None)
                raise PayUError(
                    "PayU request failed",
                    status=status,
                    payload=detail,
                    headers=dict(getattr(e.response, "headers", {}) or {}),
                    text=text,
                ) from e

        # theoretically unreachable
        raise PayUError("PayU unknown error", payload=str(last_exc) if last_exc else None)

    # ========= Utils =========

    @staticmethod
    def to_grosze(amount_pln: float) -> str:
        return str(int(round(amount_pln * 100)))

    @staticmethod
    def build_ext_order_id(prefix: str = "sub") -> str:
        return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}"


    # в PayUClient
    async def confirm_order_completed(self, order_id: str) -> dict:
        url = f"{self.cfg.base_url}/api/v2_1/orders/{order_id}/status"
        body = {"order": {"status": "COMPLETED"}}
        return await self._request_json("PUT", url, body=body)


    async def create_initial_order(
        self,
        *,
        customer_ip: str,                 # <— обязателен
        total_pln: float,
        description: str,
        notify_url: str,
        continue_url: str,
        currency: str="PLN",
        ext_order_id: Optional[str] = None,
        recurring: Optional[str] = "FIRST",
        buyer: Optional[Dict[str, Any]] = None,
        products: Optional[Iterable[Dict[str, Any]]] = None,
        pay_methods: Optional[Dict[str, Any]] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.cfg.base_url}/api/v2_1/orders"

        total = self.to_grosze(total_pln)  # string
        order: Dict[str, Any] = {
            "notifyUrl": notify_url,
            "continueUrl": continue_url,
            "customerIp": customer_ip,          # <— ТУТ ЯВНО
            "merchantPosId": self.cfg.pos_id,
            "description": description,
            "currencyCode": currency or "PLN",
            "totalAmount": total,
            "products": list(products) if products else [
                {"name": description, "unitPrice": total, "quantity": "1"}
            ],
        }
        if ext_order_id:
            order["extOrderId"] = ext_order_id
        if buyer:
            order["buyer"] = buyer
        if pay_methods:
            order["payMethods"] = pay_methods
        if recurring:
            # допустимые значения по GPO: "FIRST" или "STANDARD"
            order["recurring"] = recurring
        if extra_fields:
            order.update(extra_fields)

        return await self._request_json("POST", url, body=order, retry_on_401=True, extra_headers=extra_headers)
        
    
    async def charge_with_token(
        self,
        card_token: str,
        total_pln: float,
        description: str,
        notify_url: str,
        *,
        currency: str="PLN",
        ext_order_id: Optional[str] = None,
        products: Optional[Iterable[Dict[str, Any]]] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Автосписание (MIT) по сохранённому токену карты (CARD_TOKEN).
        """
        url = f"{self.cfg.base_url}/api/v2_1/orders"

        body: Dict[str, Any] = {
            "notifyUrl": notify_url,
            "customerIp": "127.0.0.1",
            "merchantPosId": self.cfg.pos_id,
            "description": description,
            "currencyCode": currency or "PLN",
            "totalAmount": self.to_grosze(total_pln),
            "recurring": "STANDARD",
            "payMethods": {
                "payMethod": {"type": "CARD_TOKEN", "value": card_token}
            },
            "products": list(products) if products else [
                {"name": description, "unitPrice": self.to_grosze(total_pln), "quantity": "1"}
            ],
        }
        if ext_order_id:
            body["extOrderId"] = ext_order_id
        if extra_fields:
            body.update(extra_fields)

        return await self._request_json(
            "POST",
            url,
            body=body,
            retry_on_401=True,
            extra_headers=extra_headers,
        )

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        url = f"{self.cfg.base_url}/api/v2_1/orders/{order_id}"
        return await self._request_json("GET", url)

    # ========= Webhook signature =========

    @staticmethod
    def parse_openpayu_signature(header_value: str) -> Dict[str, str]:
        parts = [p.strip() for p in (header_value or "").split(";") if p.strip()]
        out: Dict[str, str] = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                out[k.strip()] = v.strip()
        return out

    def verify_webhook(self, header_value: str, raw_body: bytes) -> bool:
        """
        Проверка OpenPayU-Signature. Поддержаны MD5 и HMAC_SHA256.
        """
        try:
            meta = self.parse_openpayu_signature(header_value)
            signature = meta.get("signature")
            algo = (meta.get("algorithm") or "MD5").upper()
            if not signature:
                return False

            if algo == "MD5":
                m = hashlib.md5()
                m.update(raw_body + self.cfg.second_key.encode("utf-8"))
                return m.hexdigest() == signature

            if algo in {"SHA256", "HMAC_SHA256"}:
                mac = hmac.new(self.cfg.second_key.encode("utf-8"), raw_body, hashlib.sha256)
                return mac.hexdigest() == signature

            # Fallback: пробуем оба
            m = hashlib.md5()
            m.update(raw_body + self.cfg.second_key.encode("utf-8"))
            if m.hexdigest() == signature:
                return True
            mac = hmac.new(self.cfg.second_key.encode("utf-8"), raw_body, hashlib.sha256)
            return mac.hexdigest() == signature
        except Exception:
            return False


# ========= Singleton factory =========

_client: Optional[PayUClient] = None

def init_payu() -> PayUClient:
    """
    Инициализирует и возвращает один глобальный экземпляр PayUClient.
    Использование из bot/bot.py:
        bot['payu'] = init_payu()
    """
    global _client
    if _client is not None:
        return _client

    cfg = PayUConfig(
        pos_id=PAYU_POS_ID,
        client_id=PAYU_CLIENT_ID,
        client_secret=PAYU_CLIENT_SECRET,
        second_key=PAYU_SECOND_KEY,
        sandbox=PAYU_SANDBOX,
    )
    _client = PayUClient(cfg)
    return _client
