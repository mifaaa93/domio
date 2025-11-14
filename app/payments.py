# app/payments.py
from __future__ import annotations

import asyncio
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from fastapi import APIRouter, Request

from app.deps import Db, PayUClientDep  # Db = Annotated[AsyncSession, Depends(db_session_dep)]
from config import LOG_DIR, PAYU_SANDBOX, SUBSCRIBES_CHANNEL
from db.models import InvoiceStatus, InvoiceType, MessageType, ChatType, User
from db.repo_async import (
    attach_payu_order_refs,
    get_invoice_by_ext_order_id,
    get_invoice_by_order_id,
    link_card_token_to_invoice,
    mark_confirmed_now,
    record_webhook_snapshot,
    upsert_card_token,
    get_user_by_token,
    add_sub_to_user,
    schedule_message
)
from db.session import get_async_session  
from payu.payu_client import PayUClient


# === ЛОГГЕР ===
os.makedirs(LOG_DIR, exist_ok=True)


def _get_logger(name: str = "payu.webhook") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fh = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "payu_webhook.log"),
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(fh)
    logger.propagate = False
    return logger


log = _get_logger()
router = APIRouter()


@router.post("/upay")
async def payu_notify(
    request: Request,
    session: Db,            # не используем в фоне — просто чтобы dependency инициализировалась
    payu: PayUClientDep,    # клиент PayU из app.state
):
    raw = await request.body()
    raw_text = raw.decode("utf-8", errors="replace")

    # подпись (варианты заголовка)
    openpayu_signature = (
        request.headers.get("OpenPayU-Signature")
        or request.headers.get("openpayu-signature")
        or request.headers.get("X-OpenPayU-Signature")
        or request.headers.get("x-openpayu-signature")
    )
    signature_valid = bool(openpayu_signature) and payu.verify_webhook(openpayu_signature, raw)

    # JSON payload
    try:
        payload = json.loads(raw_text) if raw_text else {}
    except Exception:
        payload = {"_raw": raw_text}

    order = payload.get("order") or {}
    order_id = order.get("orderId")
    ext_order_id = order.get("extOrderId")
    status = order.get("status")
    pos_id = order.get("merchantPosId")

    if pos_id and pos_id != str(payu.cfg.pos_id):
        log.warning("POS mismatch: got %s expected %s (orderId=%s)", pos_id, payu.cfg.pos_id, order_id)

    log.info(
        "Webhook received: signature_valid=%s, orderId=%s, extOrderId=%s, status=%s",
        signature_valid,
        order_id,
        ext_order_id,
        status,
    )

    # — ВАЖНО —
    # В фоне открываем свою AsyncSession из фабрики; не используем сессию запроса.
    asyncio.create_task(_process_payu_event(payu, signature_valid, payload))

    # Быстрый ответ PayU
    return {"ok": True, "signature_valid": signature_valid}


async def _process_payu_event(
    payu: PayUClient,
    signature_valid: bool,
    payload: dict,
) -> None:
    """
    Фон: идемпотентно обновить Invoice, сохранить PAYMENT_ID/RAW, автоконфирм (sandbox),
    при COMPLETED — получить CARD_TOKEN и привязать к инвойсу/пользователю.
    """
    order = payload.get("order") or {}
    order_id: Optional[str] = order.get("orderId")
    ext_order_id: Optional[str] = order.get("extOrderId")
    status_str: str = (order.get("status") or "").upper()

    properties = payload.get("properties") or []
    payment_id = next((p.get("value") for p in properties if p.get("name") == "PAYMENT_ID"), None)

    if not order_id:
        log.warning("No orderId in webhook, extOrderId=%s", ext_order_id)
        return

    async with get_async_session() as session:  # собственная сессия для фоновой задачи
        try:
            inv = await get_invoice_by_order_id(session, order_id)
            if not inv and ext_order_id:
                inv = await get_invoice_by_ext_order_id(session, ext_order_id)

            if not inv:
                log.warning("Invoice not found for orderId=%s extOrderId=%s", order_id, ext_order_id)
                return

            # Сохраняем PAYMENT_ID и снапшот вебхука
            await attach_payu_order_refs(session, inv.id, payment_id=payment_id, payu_raw=payload)

            # Продвигаем статус, если валиден
            if status_str in InvoiceStatus.__members__:
                await record_webhook_snapshot(session, inv, payu_raw=None, status=InvoiceStatus[status_str])

            # Автоконфирм в песочнице на WAITING_FOR_CONFIRMATION
            if signature_valid and status_str == "WAITING_FOR_CONFIRMATION":
                print("WAITING_FOR_CONFIRMATION")
                try:
                    resp = await payu.confirm_order_completed(order_id)
                    await mark_confirmed_now(session, inv)
                    log.info("Order confirmed → COMPLETED (orderId=%s): %s", order_id, resp.get("status"))
                except Exception:
                    log.exception("Confirm failed for orderId=%s", order_id)

            # При COMPLETED — извлечь/добрать CARD_TOKEN и привязать к инвойсу
            if status_str == "COMPLETED" and inv.user_id:
                try:
                    # иногда токен приходит прямо в вебхуке, чаще — через GET /orders/{id}
                    order_full = await payu.get_order(order_id)
                    token = (
                        (order.get("payMethod") or {}).get("value")
                        or next(
                            (p.get("value") for p in (order_full.get("properties") or []) if p.get("name") == "CARD_TOKEN"),
                            None,
                        )
                        or (((order_full.get("order") or {}).get("payMethods") or {}).get("payMethod") or {}).get("value")
                    )
                    if token:
                        ct = await upsert_card_token(session, inv.user_id, token)
                        await link_card_token_to_invoice(session, inv, ct)
                except Exception:
                    log.exception("Failed to fetch/link CARD_TOKEN for orderId=%s", order_id)
                try:
                    user: User = await get_user_by_token(session, inv.user_id)
                    if user:
                        if inv.invoice_type == InvoiceType.SUBSCRIPTION:
                            # добавляем подписку юзеру
                            await add_sub_to_user(session, user, inv.days, inv.amount, inv.is_test)
                            await schedule_message(
                                session,
                                MessageType.INVOICE,
                                chat_type=ChatType.PRIVATE,
                                payload={"from": "upay", "days": inv.days, "sub_type": "done"},
                                user_id=user.id
                                )
                            await schedule_message(
                                session,
                                MessageType.INVOICE,
                                chat_type=ChatType.CHANNEL,
                                payload={"from": "upay", "days": inv.days, "sub_type": "done"},
                                user_id=user.id,
                                chat_id=SUBSCRIBES_CHANNEL
                                )
                        if inv.invoice_type == InvoiceType.ONE_TIME:
                            # юзер приобрел что-то другое (не подписка)
                            if inv.subscribe_type == "guides":
                                # оплата гайда
                                user.is_paid = True
                                # добавить запланированные сообщения
                                await schedule_message(
                                    session,
                                    MessageType.INVOICE,
                                    chat_type=ChatType.PRIVATE,
                                    payload={"from": "upay", "sub_type": "guides"},
                                    user_id=user.id
                                    )
                                await schedule_message(
                                    session,
                                    MessageType.INVOICE,
                                    chat_type=ChatType.CHANNEL,
                                    payload={"from": "upay", "sub_type": "guides"},
                                    user_id=user.id,
                                    chat_id=SUBSCRIBES_CHANNEL
                                    )



                except Exception:
                    log.exception("Failed to add sub for user orderId=%s", order_id)
            await session.commit()
        except Exception:
            await session.rollback()
            log.exception("Background processing failed for orderId=%s", order_id)
