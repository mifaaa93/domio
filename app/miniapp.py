from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from app.deps import Db, Auth, JsonDict, PayUClientDep, Request
from db.models import Listing, User, SavedListing, MessageType, ChatType
from db.repo_async import *
from config import TARIFFS_DICT, UPAY_CALL_URL, BOT_URL
from app.ip_detect import _detect_ip




router = APIRouter()



@router.get("/count")
async def listings_count(session: Db, auth_user: Auth):
    total = await session.scalar(select(func.count()).select_from(Listing))
    return {
        "total": int(total or 0),
        "user": auth_user.get("user"),  # пример использования
    }


@router.post("/apartments")
async def get_apartments(data: JsonDict, session: Db, auth_user: Auth):
    """
    
    """
    page = data.get("page")
    cat = data.get('cat', 'listing')
    lang = data.get('lang')
    sort_field = data.get('sort_field')
    sort_dir = data.get('sort_dir')
    user_data: dict = auth_user.get("user", {})
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await get_user_by_token(session, user_data.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    apartments = await get_apartments_for_user(session, user, page, cat, lang, sort_field, sort_dir)  # верни список словарей

    return apartments


@router.post("/toggle_save")
async def toggle_save(data: JsonDict, session: Db, auth_user: Auth):
    base_id = data.get("base_id")
    action = data.get("action")

    user_data: dict = auth_user.get("user", {})
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ✅ заранее грузим коллекцию saved_listing_objs (и вложенные listing, чтобы работала проверка 'in')
    user = await session.scalar(
        select(User)
        .options(
            selectinload(User.saved_listing_objs).selectinload(SavedListing.listing)
        )
        .where(User.id == user_data["id"])
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    adv = await get_listing_by_id(session, base_id)
    if not adv:
        raise HTTPException(status_code=410, detail="Deleted Advert")

    if action == "save":
        if adv in user.saved_listings:
            status = "already_saved"
        else:
            user.saved_listings.append(adv)  # association_proxy создаст SavedListing(...)
            status = "saved"

    elif action == "remove":
        if adv in user.saved_listings:
            user.saved_listings.remove(adv)
            status = "removed"
        else:
            status = "already_removed"
    else:
        raise HTTPException(status_code=400, detail="Unknown action")

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        status = "already_saved" if action == "save" else "already_removed"

    return {"status": status, "base_id": adv.id}


@router.post("/get_link")
async def get_link(data: JsonDict, session: Db, auth_user: Auth):

    base_id = data.get("base_id")
    user_data: dict = auth_user.get("user", {})
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await get_user_by_token(session, user_data.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    adv = await get_listing_by_id(session, base_id)
    if not user.subscribed:
        raise HTTPException(status_code=403, detail="Forbiden")
    if not adv:
        raise HTTPException(status_code=410, detail="Deleted Advert")
    
    return {"url": adv.url, "base_id": adv.id}


@router.post("/trigger_invoice")
async def triger_invoice_url(data: JsonDict, session: Db, auth_user: Auth):
    
    user_data: dict = auth_user.get("user", {})
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await get_user_by_token(session, user_data.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    message = await schedule_message(
        session=session,
        message_type=MessageType.INVOICE,
        chat_type=ChatType.PRIVATE,
        payload=data,
        user_id=user.id)
    
    return {"status": message.status}


@router.post("/invoices/create")
async def create_invoice_api(
    request: Request,
    data: JsonDict,                      # ← сразу qsPayload
    session: Db,
    auth_user: Auth,
    payu: PayUClientDep,
):
    user_data = auth_user.get("user")
    if not user_data:
        raise HTTPException(401, "Unauthorized")
    user = await get_user_by_token(session, user_data.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # нормализуем вход
    subscribe_type = data.get("subscribe_type")
    invoice_type_s = data.get("invoice_type")
    try:
        invoice_type = InvoiceType(invoice_type_s)
    except Exception:
        raise HTTPException(400, "Invalid invoice type")

    invice_data: dict = TARIFFS_DICT.get(invoice_type_s, {}).get(subscribe_type)
    if not invice_data:
        raise HTTPException(400, "Unknown subscribe_type")

    client_ip = _detect_ip(request)  # IP берём на бэке

    # 1) Создаём запись инвойса в БД (status=CREATED)
    amount = float(invice_data["price"])
    days = int(invice_data["days"])
    description = invice_data.get("description") or f"Domio {subscribe_type}"
    currency = invice_data.get("currency")
    is_test = invice_data.get("is_test", True)
    next_sub = invice_data.get("next_sub")

    invoice = await create_invoice(
        session,
        user_id=user.id,
        invoice_type=invoice_type,
        amount=amount,
        currency=currency,
        description=description,
        days=days,
        client_ip=client_ip,
        subscribe_type=subscribe_type,
        is_test=is_test,
        next_sub=next_sub
    )
    if invoice.redirect_uri is None:
        # корелляционный ext_order_id, завязанный на id инвойса
        ext_order_id = payu.build_ext_order_id(prefix=f"inv{invoice.id}")
        await attach_payu_order_refs(session, invoice.id, ext_order_id=ext_order_id)
        await session.commit()
        
        try:
            order_resp: dict = await payu.create_initial_order(
                customer_ip=client_ip,            # если есть реальный IP — подставь
                total_pln=amount,             # PayU возьмёт гроши внутри
                description=description,
                notify_url=UPAY_CALL_URL,
                continue_url=BOT_URL,
                ext_order_id=ext_order_id,
                buyer=user.buyer,
                recurring="FIRST",                  # важно для токена карты
            )
        except Exception as e:
            # откат или сообщение юзеру
            raise HTTPException(400, "Can not create Invoice")

        redirect_uri = order_resp.get("redirectUri")
        order_id = order_resp.get("orderId")
        if not redirect_uri or not order_id:
            raise HTTPException(400, "Invalid redirect_uri or order_id")
        # 3) Сохраняем PayU-идентификаторы и raw-ответ, статус → PENDING
        await attach_payu_order_refs(
            session,
            invoice.id,
            order_id=order_id,
            payu_raw=order_resp,
            redirect_uri=redirect_uri,
        )
        await session.commit()
    else:
        redirect_uri = invoice.redirect_uri

    return {"redirectUri": redirect_uri}