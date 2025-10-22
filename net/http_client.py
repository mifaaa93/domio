# net/http_client.py
from __future__ import annotations
import logging
import random
import time
from typing import Any, Dict, Optional
from config import HTTP_TIMEOUT, HTTP_MAX_RETRIES, HTTP_RETRY_STATUSES, HTTP_BACKOFF_BASE, HTTP_SKEEP_STATUSES
from config import PROXIES_POOL, PROXIES_HOST, PROXIES_PASS, PROXIES_PORT, PROXIES_USERNAME

from curl_cffi import requests as crequests

logger = logging.getLogger("net")


def _choose_proxy() -> Optional[Dict[str, str]]:
    """Выбираем случайный прокси из пула. Возвращаем dict как ждёт curl_cffi.requests."""
    if not PROXIES_POOL:
        return None
    p = random.choice(PROXIES_POOL)
    if not p:
        return None
    p = f"http://{PROXIES_USERNAME}-ip-{p}:{PROXIES_PASS}@{PROXIES_HOST}:{PROXIES_PORT}"
    # Одинаково задаём и для http, и для https
    return {"http": p, "https": p}


def _sleep_backoff(attempt: int) -> None:
    """Экспоненциальный backoff с джиттером."""
    delay = HTTP_BACKOFF_BASE * (2 ** (attempt - 1))
    jitter = random.uniform(0, 0.5)
    time.sleep(delay + jitter)


async def fetch_status(url: str, headers: dict=None) -> int:
    """"""
    async with crequests.AsyncSession() as s:
        r: crequests.models.Response = await s.get(
            url,
            timeout=20,
            headers=headers,
            proxies=_choose_proxy())
        return r.status_code


def http_request(
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Any = None,
    json: Any = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_statuses: Optional[set[int]] = None,
) -> crequests.Response:
    """
    Универсальный запрос с ретраями и ротацией прокси (новый прокси на КАЖДУЮ попытку).
    Бросает исключение после исчерпания попыток.
    """
    _timeout = timeout if timeout is not None else HTTP_TIMEOUT
    _max_retries = max_retries if max_retries is not None else HTTP_MAX_RETRIES
    last_exc: Optional[BaseException] = None

    for attempt in range(1, _max_retries + 1):
        proxies = _choose_proxy()
        try:
            resp = crequests.request(
                method=method.upper(),
                url=url,
                params=params,
                headers=headers,
                data=data,
                json=json,
                proxies=proxies,
                timeout=_timeout,
            )
            # 429/5xx — ретраим
            if resp.status_code in HTTP_RETRY_STATUSES:
                logger.warning(
                    "HTTP %s %s -> %s (retryable), attempt %d/%d",
                    method, url, resp.status_code, attempt, _max_retries,
                )
                if attempt < _max_retries:
                    _sleep_backoff(attempt)
                    continue
                resp.raise_for_status()
            # прочие статусы — сразу raise при необходимости (4xx и т.п.)
            elif resp.status_code in HTTP_SKEEP_STATUSES:
                last_exc = RuntimeError(f"Not found: {resp.status_code} {url}")
                break
            resp.raise_for_status()
            return resp

        except Exception as e:
            last_exc = e
            logger.warning(
                "HTTP %s %s raised %r, attempt %d/%d",
                method, url, e, attempt, _max_retries,
            )
            if attempt < _max_retries:
                _sleep_backoff(attempt)
                continue
            # исчерпали попытки
            raise

    # защитный return, по логике сюда не дойдём
    if last_exc:
        raise last_exc
    raise RuntimeError("http_request failed without exception (unexpected)")
    

# Удобные обёртки
def http_get(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_statuses: Optional[set[int]] = None,
) -> crequests.Response:
    return http_request(
        "GET", url,
        params=params, headers=headers,
        timeout=timeout,
        max_retries=max_retries,
        retry_statuses=retry_statuses,
    )


def get_json(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_statuses: Optional[set[int]] = None,
) -> dict:
    """Сразу возвращает .json() с теми же ретраями и прокси-ротацией."""
    r = http_get(
        url, params=params, headers=headers,
        timeout=timeout,
        max_retries=max_retries, retry_statuses=retry_statuses,
    )
    return r.json()
