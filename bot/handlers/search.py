# bot/handlers/search.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.repo_async import *
from bot.utils.messages import *
from config import CITIES_STR, CITIES_STR_SALE

router = Router()


@router.callback_query(F.data.startswith("search_type|"))
async def search_type_select(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    Сохраняем тип пошуку (rent/sale) и переходим к выбору типа нерухомості.
    """
    _, search_type_val = callback.data.split("|", 1)  # rent / sale
    # --- получить или создать фильтр для пользователя ---
    search = await get_user_search(session, user)
    search.deal_type = search_type_val
    await session.commit()
    if search_type_val == "rent":
        await estate_type(callback, user, deal_type=search.deal_type)
    elif search_type_val == "sale":
        await market_type(callback, user)


@router.callback_query(F.data.startswith("estate_type|"))
async def estate_type_select(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    Сохраняем тип нерухомості (apartment, house, room) и переходим к выбору типа города.
    """
    _, estate_type_val = callback.data.split("|", 1)  # apartment, house, room
    # --- получить или создать фильтр для пользователя ---
    search = await get_user_search(session, user)
    search.property_type = estate_type_val
    await session.commit()
    if search.deal_type == "rent":
        c_list = CITIES_STR
    else:
        c_list = CITIES_STR_SALE
    cities = await get_cities(session, c_list)
    await select_city(callback, user, try_edit=True, cities=cities)


@router.callback_query(F.data.startswith("market_type|"))
async def market_type_select(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    Сохраняем тип рынка для покупки и переход к выбору типа недвижимости
    """
    _, market_type_val = callback.data.split("|", 1)  # apartment, house, room
    # --- получить или создать фильтр для пользователя ---
    search = await get_user_search(session, user)
    search.market = market_type_val
    await session.commit()

    await estate_type(callback, user, deal_type=search.deal_type)


@router.callback_query(F.data.startswith("select_city|"))
async def select_city_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    Сохраняем город и переход к району
    """
    _, city_id = callback.data.split("|", 1)  # 124
    # --- получить или создать фильтр для пользователя ---
    city_id = int(city_id)
    search = await get_user_search(session, user)
    search.city_id = city_id
    await session.commit()

    all_districts = await get_districts(session, city_id)
    selected_districts = search.districts
    await select_district(
        callback,
        user,
        try_edit=True,
        all_districts=all_districts,
        selected_districts=selected_districts)
    


@router.callback_query(F.data.startswith("back_from|"))
async def back_search_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, back_from = callback.data.split("|", 1)
    search = await get_user_search(session, user)
    if back_from == "estate_type":
        # назад из меню выбора типа недвижимости
        if search.deal_type == "rent":
            await start_search(callback, user, try_edit=True)
        else:
            await market_type(callback, user, try_edit=True)
        
    elif back_from == "market_type":
        # назад из меню выбора типа рынка
        await start_search(callback, user, try_edit=True)
    
    elif back_from == "select_city":
        # назад из меню выбора города
        if search.deal_type == "rent":
            await estate_type(callback, user, deal_type=search.deal_type)
        else:
            await market_type(callback, user, try_edit=True)
    
    elif back_from == "select_district":
        # назад из меню выбора района
        if search.deal_type == "rent":
            c_list = CITIES_STR
        else:
            c_list = CITIES_STR_SALE
        cities = await get_cities(session, c_list)
        await select_city(callback, user, try_edit=True, cities=cities)
    


