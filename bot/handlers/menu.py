# bot\handlers\menu.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from bot.utils.messages import *
from bot.texts import btn_tuple
from bot.filters.m_filters import LanguageNotChosen
from db.repo_async import get_saved_listing_ids, get_cities
from config import CITIES_STR

router = Router()


@router.message(LanguageNotChosen())
async def not_choosen_language_btn(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка поиск квартир
    """
    # выбор языка
    await send_language_prompt(msg, user)


@router.message(
        F.text.in_(btn_tuple("search")))
async def search_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка поиск квартир
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await start_search(msg, user)
    await state.clear()


@router.message(
        F.text.in_(btn_tuple("subscribe")))
async def subscribe_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка подписка
    """
    # сообщение с выбором подписки
    await trigger_invoice(msg, user)
    await state.clear()


@router.message(
        F.text.in_(btn_tuple("favorites")))
async def favorites_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 💾 Збережені
    """
    if not user.is_full_sub_active:
        await only_full_sub_message(msg, user)
        await state.clear()
        return
    saved_ids = await get_saved_listing_ids(session, user)
    total = len(saved_ids)
    await favorites(msg, user, total=total)
    await state.clear()

@router.message(
        F.text.in_(btn_tuple("settings")))
async def settings_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка ⚙️ Налаштування
    """
    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await settings_main(msg, user)
    await state.clear()


@router.message(
        F.text.in_(btn_tuple("earn_with_domio")))
async def earn_with_domio_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 💰 Заробіток з Domio
    """
    # рефералка
    await earn_with_domio(msg, user)
    await state.clear()

@router.message(
        F.text.in_(btn_tuple("help")))
async def help_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 🛟 Допомога
    """
    # помощь
    await help_message(msg, user)
    await state.clear()

@router.message(
        F.text.in_(btn_tuple("reviews")))
async def reviews_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 🗣 Відгуки
    """
    # отзывы
    await reviews(msg, user)
    await state.clear()


@router.message(
        F.text.in_(btn_tuple("how_to_use")))
async def how_to_use_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 🪄 Як користуватися
    """
    # меню выбора инструкций
    await how_to_use(msg, user)
    await state.clear()


@router.message(
        F.text.in_(btn_tuple("guides")))
async def guides_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 📘 Гайди
    """
    # меню выбора инструкций
    await guides(msg, user)
    await state.clear()

@router.message(
        F.text.in_(btn_tuple("contact_agent")))
async def contact_agent_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка Контакт з ріелтором
    """
    # меню выбора инструкций
    cities = await get_cities(session, CITIES_STR)
    await contact_agent(msg, user, cities=cities)
    await state.clear()


@router.message(
        F.text.in_(btn_tuple("builders_services")))
async def builders_services_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка 🛠 Інші послуги
    """
    # меню выбора инструкций
    cities = await get_cities(session, CITIES_STR)
    await builders_services(msg, user, cities=cities)
    await state.clear()
