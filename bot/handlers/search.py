# bot/handlers/search.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.repo_async import *
from bot.texts import alert_t
from bot.utils.messages import *
from bot.utils.helpers import parse_price
from bot.states import PriceStates
from config import CITIES_STR, ADMIN_IDS

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
    if user.id in ADMIN_IDS:
        # если админ то даем выбрать без комиссии или с комиссией
        await comissiom_type(callback, user)
    else:
        # иначе переходим к выбору города
        cities = await get_cities(session, CITIES_STR)
        await select_city(callback, user, try_edit=True, cities=cities)

@router.callback_query(F.data.startswith("comissiom_type|"))
async def comissiom_type_select(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    Сохраняем тип комиссии (apartment, house, room) и переходим к выбору типа города.
    """
    _, comissiom_type_raw = callback.data.split("|", 1)  # owner, rieltor, all
    # --- получить или создать фильтр для пользователя ---
    value = None
    if comissiom_type_raw == "owner":
        value = True
    elif comissiom_type_raw == "rieltor":
        value = False
    search = await get_user_search(session, user)
    search.no_comission = value
    await session.commit()
    cities = await get_cities(session, CITIES_STR)
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
    if search.city_id != city_id:
        search.districts.clear()
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
    

@router.callback_query(F.data.startswith("select_district|"))
async def select_district_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    добавляем или удаляем район
    """
    _, district_id = callback.data.split("|", 1)  # 124
    # --- получить или создать фильтр для пользователя ---
    district_id = int(district_id)
    search = await get_user_search(session, user)
    all_districts = await get_districts(session, search.city_id)
    district = await session.get(District, district_id)
    if district is not None:
        # Тогглим по объекту, а не по id
        if district in search.districts:
            search.districts.remove(district)
        else:
            search.districts.append(district)
        await session.commit()

    await select_district(
        callback,
        user,
        try_edit=True,
        all_districts=all_districts,
        selected_districts=search.districts,
        only_btns=True)


@router.callback_query(F.data.startswith("next_select_district|"))
async def next_select_district_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    сохраняем район и переходим к минимальной площади если это не поиск комнаты
    иначе переходим сразу к бюджету
    """
    _, all_flag = callback.data.split("|", 1)  # 124
    all_flag = bool(all_flag)
    # --- получить или создать фильтр для пользователя ---
    search = await get_user_search(session, user)
    if all_flag:
        search.districts.clear()
        await session.commit()
    
    # проверяем если поиск комнаты то переход к бюджету
    if search.property_type == "room":
        new_message = await min_price(
            callback,
            user,
            try_edit=True
            )
        await state.set_state(PriceStates.min_price)
        await state.set_data({
            "to_delete": [
                (new_message.chat.id, new_message.message_id)
                ]})
    else:
        await area_from(
        callback,
        user,
        try_edit=True)


@router.callback_query(F.data.startswith("area_from|"))
async def area_from_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    площадь от
    """
    _, area_raw = callback.data.split("|", 1)  # 124
    area_value = int(area_raw) if area_raw else None
    # --- получить или создать фильтр для пользователя ---
    search = await get_user_search(session, user)
    search.area_min = area_value
    await session.commit()
    
    await area_to(
        callback,
        user,
        try_edit=True,
        min_area=area_value)


@router.callback_query(F.data.startswith("area_to|"))
async def area_to_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    площадь до
    """
    _, area_raw = callback.data.split("|", 1)  # 124
    area_value = int(area_raw) if area_raw else None
    # --- получить или создать фильтр для пользователя ---
    search = await get_user_search(session, user)
    search.area_max = area_value
    await session.commit()
    
    await rooms_count(
        callback,
        user,
        try_edit=True,
        selected=search.rooms)


@router.callback_query(F.data.startswith("rooms_count|"))
async def rooms_count_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    количество комнат
    """
    _, rooms_raw = callback.data.split("|", 1)  # 124
    rooms_value = int(rooms_raw) if rooms_raw else None
    # --- получить или создать фильтр для пользователя ---
    search = await get_user_search(session, user)
    if rooms_value:
        current = list(search.rooms or [])
        if rooms_value in current:
            current.remove(rooms_value)
        else:
            current.append(rooms_value)
        search.rooms = current
        await session.commit()

        await rooms_count(
            callback,
            user,
            try_edit=True,
            selected=current,
            only_btns=True
            )
    else:
        if not search.rooms:
            await callback.answer(alert_t(user.language_code, "no_room_selected"), show_alert=True)
        else:
            new_message = await min_price(
                callback,
                user,
                try_edit=True
                )
            await state.set_state(PriceStates.min_price)
            await state.set_data({
                "to_delete": [
                    (new_message.chat.id, new_message.message_id)
                    ]})


@router.message(StateFilter(PriceStates.min_price))
async def handle_min_price(message: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    ожидаем от юзера ввода минимального бюджета
    """
    price = parse_price(message.text)
    await message.delete()
    if price is None:
        return
    search = await get_user_search(session, user)
    search.price_min = price
    search.price_max = None
    await session.commit()

    new_message = await max_price(
            message,
            user,
            try_edit=False
            )
    old_data = await state.get_data()
    await state.set_state(PriceStates.max_price)
    await state.set_data({
        "to_delete": [
            (new_message.chat.id, new_message.message_id)
            ]})
    if old_data:
        items = old_data.get("to_delete", [])
        for ch_id, m_id in items:
            try:
                await message.bot.delete_message(ch_id, m_id)
            except Exception as e:
                pass


@router.message(StateFilter(PriceStates.max_price))
async def handle_max_price(message: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    ожидаем от юзера ввода максимального бюджета
    """
    price = parse_price(message.text)
    await message.delete()
    if price is None:
        return
    search = await get_user_search(session, user)
    search.price_max = price
    if search.price_min is not None:
        if search.price_min >= price:
            search.price_min = None
    if search.deal_type == "sale":
        search.has_confirmed_policy = True
    await session.commit()

    old_data = await state.get_data()
    await state.clear()
    if old_data:
        items = old_data.get("to_delete", [])
        for ch_id, m_id in items:
            try:
                await message.bot.delete_message(ch_id, m_id)
            except Exception as e:
                pass
    
    # если покупка то переходим к результатам
    # если аренда то вопрос про детей
    if search.deal_type == "rent":
        await child(
            message,
            user,
            try_edit=False
        )
    else:
        _, total = await find_listings_by_search(session, search, return_total=True)
        await show_results(
            message,
            user,
            try_edit=False,
            total=total,
            search=search
        )


@router.callback_query(F.data.startswith("min_price|"))
async def min_price_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    любая цена
    """
    _, min_price_raw = callback.data.split("|", 1)  # 124
    search = await get_user_search(session, user)
    search.price_min = None
    await session.commit()

    new_message = await max_price(
            callback,
            user,
            try_edit=True
            )
    await state.set_state(PriceStates.max_price)
    await state.set_data({
        "to_delete": [
            (new_message.chat.id, new_message.message_id)
            ]})


@router.callback_query(F.data.startswith("max_price|"))
async def min_price_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    любая цена 
    """
    _, max_price_raw = callback.data.split("|", 1)  # 124
    search = await get_user_search(session, user)
    search.price_max = None
    if search.deal_type == "sale":
        search.has_confirmed_policy = True
    await session.commit()
    await state.clear()
    
    # если покупка то переходим к результатам
    # если аренда то вопрос про детей
    if search.deal_type == "rent":
        await child(
            callback,
            user,
            try_edit=True
        )
    else:
        _, total = await find_listings_by_search(session, search, return_total=True)
        await show_results(
            callback,
            user,
            try_edit=True,
            total=total,
            search=search
        )
    
@router.callback_query(F.data.startswith("child|"))
async def child_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    дети
    """
    _, value_raw = callback.data.split("|", 1)  # 124
    yes = value_raw == "yes"
    search = await get_user_search(session, user)
    search.child_allowed = yes
    await session.commit()
   
    # если покупка то переходим к результатам
    # если аренда то вопрос про детей
    await pets(
            callback,
            user,
            try_edit=True
        )


@router.callback_query(F.data.startswith("pets|"))
async def pets_call(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """
    животные
    """
    _, value_raw = callback.data.split("|", 1)  # 124
    yes = value_raw == "yes"
    search = await get_user_search(session, user)
    search.pets_allowed = yes
    search.has_confirmed_policy = True
    await session.commit()
    _, total = await find_listings_by_search(session, search, return_total=True)
    await show_results(
            callback,
            user,
            try_edit=True,
            total=total,
            search=search
        )


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
    
    elif back_from == "comissiom_type":
        # назад из меню выбора типа рынка
        await estate_type(callback, user, try_edit=True)
    
    elif back_from == "select_city":
        # назад из меню выбора города
        if user.id in ADMIN_IDS:
        # если админ то даем выбрать без комиссии или с комиссией
            await comissiom_type(callback, user)
        else:
            await estate_type(callback, user, deal_type=search.deal_type)

    elif back_from == "select_district":
        # назад из меню выбора района
        cities = await get_cities(session, CITIES_STR)
        await select_city(callback, user, try_edit=True, cities=cities)
    
    elif back_from == "area_from":
        # назад с меню выбора мин площади
        all_districts = await get_districts(session, search.city_id)
        selected_districts = search.districts
        await select_district(
            callback,
            user,
            try_edit=True,
            all_districts=all_districts,
            selected_districts=selected_districts)
    
    elif back_from == "area_to":
        # назад с меню выбора макс площади
        await area_from(
            callback,
            user,
            try_edit=True)
    
    elif back_from == "rooms_count":
        # назад с меню выбора макс площади
        await area_to(
            callback,
            user,
            try_edit=True,
            min_area=search.area_min)
    
    elif back_from == "min_price":
        # назад с ввода минимального бюджета
        # идем или к выбору количества комнат или к выбору района если это поиск комнат
        await state.clear()
        if search.property_type == "room":
            all_districts = await get_districts(session, search.city_id)
            selected_districts = search.districts
            await select_district(
                callback,
                user,
                try_edit=True,
                all_districts=all_districts,
                selected_districts=selected_districts)
        else:
            await rooms_count(
                callback,
                user,
                try_edit=True,
                selected=search.rooms)
    
    elif back_from == "max_price":
        # назад с ввода максимального бюджета
        # идем к выбору минимального бюджета
        new_message = await min_price(
                callback,
                user,
                try_edit=True
                )
        await state.set_state(PriceStates.min_price)
        await state.set_data({
            "to_delete": [
                (new_message.chat.id, new_message.message_id)
                ]})
    
    elif back_from == "child":
        # назад с выбора наличия детей
        # идем к выбору минимального бюджета
        new_message = await max_price(
                callback,
                user,
                try_edit=True
                )
        await state.set_state(PriceStates.max_price)
        await state.set_data({
            "to_delete": [
                (new_message.chat.id, new_message.message_id)
                ]})
    
    elif back_from == "pets":
        # назад с выбора наличия детей
        # идем к выбору минимального бюджета
        await child(
            callback,
            user,
            try_edit=True
        )
