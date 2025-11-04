from fastapi import Request
import re

# Простой валидатор IPv4/IPv6 (без строгих проверок портов/брекетов)
_IP_RE = re.compile(
    r"""
    ^\s*
    (?:                                  # IPv4
        (?:\d{1,3}\.){3}\d{1,3}
    |
        \[?[A-Fa-f0-9:]+\]?              # IPv6 (возможно в [])
    )
    \s*$
    """,
    re.X,
)

def _parse_forwarded_header(val: str) -> list[str]:
    """
    RFC 7239 Forwarded: for=1.2.3.4, for="[2001:db8:cafe::17]"
    Возвращает список IP из параметров 'for=' в том порядке, как пришли.
    """
    if not val:
        return []
    out: list[str] = []
    # Разбиваем по запятым — это прокси-цепочка
    parts = [p.strip() for p in val.split(",")]
    for p in parts:
        # Ищем ключ for=..., допускаем кавычки
        m = re.search(r'for=\s*("?)([^;," ]+)\1', p, re.I)
        if not m:
            continue
        ip = m.group(2)
        # Снимем возможные квадратные скобки у IPv6
        if ip.startswith("[") and ip.endswith("]"):
            ip = ip[1:-1]
        out.append(ip)
    return out

def _split_xff(val: str) -> list[str]:
    """
    X-Forwarded-For: client, proxy1, proxy2
    Возвращает список IP в исходном порядке.
    """
    if not val:
        return []
    parts = [p.strip() for p in val.split(",") if p.strip()]
    # Чистим [] у IPv6
    cleaned = []
    for ip in parts:
        if ip.startswith("[") and ip.endswith("]"):
            ip = ip[1:-1]
        cleaned.append(ip)
    return cleaned

def _is_ip(s: str) -> bool:
    return bool(s and _IP_RE.match(s))

def _detect_ip(request: Request) -> str:
    """
    Пытается определить реальный IP клиента с учётом прокси/CDN.
    Порядок приоритета:
      1) Forwarded (RFC 7239) → for=...
      2) X-Forwarded-For (первый в цепочке)
      3) CF-Connecting-IP / True-Client-IP / X-Real-IP
      4) request.client.host
    Возвращает строку IP (IPv4/IPv6). Если ничего не нашли — '127.0.0.1'.
    """
    headers = request.headers

    # 1) RFC 7239
    fwd = headers.get("Forwarded") or headers.get("forwarded")
    for ip in _parse_forwarded_header(fwd):
        if _is_ip(ip):
            return ip

    # 2) X-Forwarded-For (первый элемент — исходный клиент)
    xff = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
    for ip in _split_xff(xff):
        if _is_ip(ip):
            return ip

    # 3) Популярные CDN/прокси заголовки
    for h in ("CF-Connecting-IP", "True-Client-IP", "X-Real-IP",
              "cf-connecting-ip", "true-client-ip", "x-real-ip"):
        ip = headers.get(h)
        if _is_ip(ip or ""):
            # снимаем [] у IPv6, если вдруг
            if ip.startswith("[") and ip.endswith("]"):
                ip = ip[1:-1]
            return ip

    # 4) Сокетный адрес
    sock_ip = getattr(getattr(request, "client", None), "host", None)
    if _is_ip(sock_ip or ""):
        return sock_ip  # type: ignore[return-value]

    return "127.0.0.1"
