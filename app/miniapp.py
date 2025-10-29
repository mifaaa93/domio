from typing import Annotated, Any
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from app.deps import db_session_dep
from app.validator import valid_user_from_header, MiniAppAuth
from db.models import Listing, User, SavedListing
from db.repo_async import *
from bot.bot import sender_bot
from bot.utils.messages import trigger_invoice



router = APIRouter()

Db = Annotated[AsyncSession, Depends(db_session_dep)]
Auth = Annotated[MiniAppAuth, Depends(valid_user_from_header)]
JsonDict = Annotated[dict[str, Any], Body(...)]  # обязателен JSON в теле


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
    page = int(data.get("page", 1))
    cat = data.get('cat', 'all')
    user_data: dict = auth_user.get("user", {})
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await get_user_by_token(session, user_data.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    apartments = await get_apartments_for_user(session, user, page, cat)  # верни список словарей

    return apartments


@router.post("/toggle_save")
async def toggle_save(data: JsonDict, session: Db, auth_user: Auth):
    
    base_id = data.get("base_id")
    action = data.get("action")

    user_data: dict = auth_user.get("user", {})
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await get_user_by_token(session, user_data.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    adv = await get_listing_by_id(session, base_id)
    if not adv:
        raise HTTPException(status_code=410, detail="Deleted Advert")

    saved_exists = await session.scalar(
        select(exists().where(
            (SavedListing.user_id == user.id) &
            (SavedListing.listing_id == adv.id)
        ))
    )

    # 5) Операция
    if action == "save":
        if saved_exists:
            status = "already_saved"
        else:
            # association_proxy создаст SavedListing(...)
            user.saved_listings.append(adv)
            status = "saved"

    elif action == "remove":
        if not saved_exists:
            # делаем идемпотентным
            status = "already_removed"
        else:
            # безопасное удаление через proxy: найдём объект и удалим
            # (можно и через DELETE ... WHERE user_id/listing_id)
            # найдём объект SavedListing (точечный)
            sl = await session.scalar(
                select(SavedListing).where(
                    (SavedListing.user_id == user.id) &
                    (SavedListing.listing_id == adv.id)
                )
            )
            if sl:
                await session.delete(sl)
            status = "removed"
    # 6) Коммит (важно!)
    try:
        await session.commit()
    except IntegrityError:
        # На случай гонок (в параллели уже добавили): делаем идемпотент
        await session.rollback()
        if action == "save":
            status = "already_saved"
        else:
            status = "already_removed"

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
    
    message = await trigger_invoice(user, sender_bot)
    
    return {"status": message.message_id}