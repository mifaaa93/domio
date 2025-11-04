# bot\handlers\menu.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from bot.utils.messages import *
from bot.texts import btn_tuple
from db.repo_async import get_saved_listing_ids

router = Router()


@router.message(F.text.in_(btn_tuple("search")))
async def search_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка поиск квартир
    """
    if user.language_code is None:
        await send_language_prompt(msg, user)
        return

    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await start_search(msg, user)


@router.message(F.text.in_(btn_tuple("subscribe")))
async def subscribe_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка подписка
    """
    if user.language_code is None:
        await send_language_prompt(msg, user)
        return

    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await trigger_invoice(msg, user)


@router.message(F.text.in_(btn_tuple("favorites")))
async def favorites_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 💾 Збережені
    """
    if user.language_code is None:
        await send_language_prompt(msg, user)
        return
    saved_ids = await get_saved_listing_ids(session, user)
    total = len(saved_ids)
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await favorites(msg, user, total=total)