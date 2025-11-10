from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

from db.models import User, SavedListing
from db.repo_async import get_listing_by_id, get_saved_listing_ids
from bot.utils.messages import *
from bot.texts import alert_t
from bot.keyboards.listing import get_under_listing_btns

router = Router()


@router.callback_query(F.data.startswith("settings|"))
async def choose_language(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, submenu = callback.data.split("|", 1)
    
    if submenu == "language":
        # смена языка
        await send_language_prompt(callback, user, True)
    
    elif submenu == "recurring":
        # отключение автопродления
        await send_recurring_prompt(callback, user, True)
    
    elif submenu == "settings":
        # кнопка назад в настройки
        await settings_main(callback, user, True)



@router.callback_query(F.data.startswith("lang|"))
async def choose_language(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    изменение языка
    """
    lang_code = callback.data.split("|", 1)[1]
    user.language_code = lang_code
    session.add(user)
    await session.commit()
    
    await send_language_set(callback, user)
    await send_main_menu(callback, user)


@router.callback_query(F.data.startswith("recurring|"))
async def recurring_disable_confirmed(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    юзер нажал кнопку подтвердить отключение автопродления
    """
    _, off = callback.data.split("|", 1)
    if off == "off":
        user.recurring_on = False
        session.add(user)
        await session.commit()
    await callback.answer(
        text=alert_t(user.language_code, "recurring_disable_confirmed"),
        show_alert=True)
    await settings_main(callback, user, True)


@router.callback_query(F.data.startswith("listing|"))
async def listing_like_unlike(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, submenu = callback.data.split("|", 1) # unlike|id like|id

    if submenu.startswith(("unlike", "like",)):
        if not user.is_full_sub_active:
            await callback.answer(
                alert_t(user.language_code, "not_aval_in_test"),
                show_alert=True
            )
            return
        what_task, base_id = submenu.split("|", 1)
        base_id = int(base_id)
        adv = await get_listing_by_id(session, base_id)
        if not adv:
            await callback.answer(
                text=alert_t(user.language_code, "listing_deleted"),
                show_alert=True)
            await callback.message.delete()
            return
        
        user = await session.scalar(
            select(User)
            .options(
                selectinload(User.saved_listing_objs).selectinload(SavedListing.listing)
            )
            .where(User.id == user.id)
        )
        if what_task == "like":
            if adv not in user.saved_listings:
                user.saved_listings.append(adv)
                await session.commit()

        elif what_task == "unlike":
            if adv in user.saved_listings:
                user.saved_listings.remove(adv)
                await session.commit()

        saved_ids = await get_saved_listing_ids(session, user)
        btns = get_under_listing_btns(adv, user, saved_ids)
        await edit_btns(callback, btns)
