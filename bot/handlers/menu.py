# bot\handlers\menu.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from bot.utils.messages import *
from bot.texts import btn_tuple
from bot.filters.m_filters import LanguageNotChosen
from db.repo_async import get_saved_listing_ids

router = Router()


@router.message(LanguageNotChosen())
async def not_choosen_language_btn(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка поиск квартир
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await send_language_prompt(msg, user)


@router.message(
        F.text.in_(btn_tuple("search")))
async def search_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка поиск квартир
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await start_search(msg, user)


@router.message(
        F.text.in_(btn_tuple("subscribe")))
async def subscribe_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка подписка
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await trigger_invoice(msg, user)


@router.message(
        F.text.in_(btn_tuple("favorites")))
async def favorites_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 💾 Збережені
    """
    saved_ids = await get_saved_listing_ids(session, user)
    total = len(saved_ids)
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await favorites(msg, user, total=total)

@router.message(
        F.text.in_(btn_tuple("settings")))
async def settings_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка ⚙️ Налаштування
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await settings_main(msg, user)


@router.message(
        F.text.in_(btn_tuple("earn_with_domio")))
async def earn_with_domio_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 💰 Заробіток з Domio
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await earn_with_domio(msg, user)

@router.message(
        F.text.in_(btn_tuple("help")))
async def help_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 🛟 Допомога
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await help_message(msg, user)

@router.message(
        F.text.in_(btn_tuple("reviews")))
async def reviews_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 🗣 Відгуки
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await reviews(msg, user)