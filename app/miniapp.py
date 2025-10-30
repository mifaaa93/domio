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
    page = data.get("page")
    cat = data.get('cat', 'listing')
    lang = data.get('lang')
    user_data: dict = auth_user.get("user", {})
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await get_user_by_token(session, user_data.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    apartments = await get_apartments_for_user(session, user, page, cat, lang)  # верни список словарей

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
    
    message = await trigger_invoice(user=user, bot=sender_bot)
    
    return {"status": message.message_id}