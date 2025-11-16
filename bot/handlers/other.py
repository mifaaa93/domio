from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from config import REFERAL_CHANNEL, CITIES_STR, SERVICES_CHANNELS

from db.models import User, MessageType, ChatType
from db.repo_async import schedule_message, get_cities, add_statistic_data
from bot.utils.messages import *
from bot.texts import alert_t, btn
from bot.states import ServiceStates, AgentStates
from html import escape


router = Router()


@router.callback_query(F.data.startswith("earn|"))
async def earn_main_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, submenu = callback.data.split("|", 1)
    
    if submenu == "instruction":
        # инструкция по реферальной программе
        await earn_instruction(callback, user, True)
    
    elif submenu == "pay_out":
        # запрос подтверждения вывода средств
        if not user.referral_balance_current:
            await callback.answer(
                text=alert_t(user.language_code, "no_ref_balance"),
                show_alert=True
            )
        else:
            await ask_earn_payout(callback, user, True)
    
    elif submenu == "confirm_earn":
        # подтвердить списание
        # запрос подтверждения вывода средств
        if not user.referral_balance_current:
            await callback.answer(
                text=alert_t(user.language_code, "no_ref_balance"),
                show_alert=True
            )
            await earn_with_domio(callback, user, True)
        else:
            # средства есть, делаем запрос на вывод
            current = user.referral_balance_current
            user.referral_balance_current = 0.0
            await session.commit()
            await schedule_message(
                    session,
                    MessageType.CUSTOM,
                    chat_type=ChatType.CHANNEL,
                    chat_id=REFERAL_CHANNEL,
                    payload={"from": "confirm_earn", "amount": current},
                    user_id=user.id
                    )
            await payout_request_sended(callback, user, current, True)

    elif submenu == "earn":
        # кнопка назад в реферальное меню
        await earn_with_domio(callback, user, True)


@router.callback_query(F.data.startswith("how_to_use|"))
async def how_to_use_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, submenu = callback.data.split("|", 1)
    
    if submenu == "how_to_use":
        # кнопка назад в реферальное меню
        await how_to_use(callback, user, True)
    
    else:
        # тут инструкция по каждому пункуту
        await send_video_instruction(callback, user, True, submenu)


@router.callback_query(F.data.startswith("guides|"))
async def guides_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, submenu = callback.data.split("|", 1)
    
    if submenu == "guides":
        # кнопка назад в в меню гайдов
        await guides(callback, user, True)
    
    elif submenu == "rent":
        # показываем подменю с гайдами по оренде
        if not user.is_full_sub_active:
            # если не полная подписка
            await callback.answer(
                alert_t(user.language_code, "not_aval_in_test"),
                show_alert=True
            )
            return
        await guides_rent(callback, user, True)

    elif submenu == "sale":
        # показываем подменю с гайдами по покупке (проверяем оплату и если оплата есть то гайд, если нету
        # то описание и кнопка оплаты)
        await guides_sale(callback, user, True)


@router.callback_query(F.data.startswith("other|"))
async def select_city_builders_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    '''
    выбор города для других услуг.
    other|other кнопка назад
    other|city|{city_id} кнопка выдор города
    other|keys|{key}|{city_id} кнопка выбор услуги в городе
    other|confirm|{key}|{city_id}
    '''
    _, command = callback.data.split("|", 1)  # city|122

    if command == "other":
        # назад к выбору города
        cities = await get_cities(session, CITIES_STR)
        await builders_services(callback, user, try_edit=True, cities=cities)

    elif command.startswith("city|"):
        # выьран город, переходим к выбору услуги
        _, city_id = command.split("|", 1)  # 124
        # --- получить или создать фильтр для пользователя ---
        await builders_type(callback, user, int(city_id), True)
        await state.clear()
    
    elif command.startswith("keys|"):
        # выьран город, переходим к выбору услуги
        _, key, city_id = command.split("|", 2)  # repair_turnkey, 123
        # --- получить или создать фильтр для пользователя ---
        city_id = int(city_id)
        city = await session.get(City, city_id)
        if not city:
            # если города нету то возвращаем к выбору городов
            cities = await get_cities(session, CITIES_STR)
            await builders_services(callback, user, try_edit=True, cities=cities)
            return
        data: dict = SERVICES_CHANNELS.get(city.name_pl, {})
        value = data.get(key)
        await add_statistic_data(session, user, "services", "click", {
            "key": key,
            "city_id": city_id,
            "work_type": btn("uk", key=key),
        })

        if value is None:
            # такой услуги в этом городе нету
            await service_not_availabel(callback, user, city_id=city_id, try_edit=True)
        else:
            if isinstance(value, str):
                # значит ключ текста контакта. отправляем его
                await send_contact_for_service(callback, user, city_id=city_id, key=value, try_edit=True)
            elif isinstance(value, int):
                # значит айди канала. продолжаем ввод 
                if key == "moving_transport":
                    # если выбор помощь для переезда то выдаем сообщение с кнопкой продолжить
                    await moving_transport_first(callback, user, city_id=city_id, key=key, try_edit=True)
                else:
                    # если другой тип то запрашиваем доп информацию и кнопка пропустить
                    new_message = await send_wait_description_service(callback, user, city_id=city_id, try_edit=True)
                    name_uk = btn("uk", key=key)
                    await state.set_state(ServiceStates.wait_description)
                    await state.set_data({
                        "to_delete": [
                            (new_message.chat.id, new_message.message_id)
                            ],
                        "channel_id": value,
                        "key": key,
                        "city": city.name_uk,
                        "city_id": city_id,
                        "work_type": name_uk})

            else:
                await callback.answer()
    
    elif command.startswith("confirm|"):
        # выьран город, переходим к выбору услуги
        _, key, city_id = command.split("|", 2)  # moving_transport, 123
        # --- получить или создать фильтр для пользователя ---
        city_id = int(city_id)
        city = await session.get(City, city_id)
        if not city:
            # если города нету то возвращаем к выбору городов
            cities = await get_cities(session, CITIES_STR)
            await builders_services(callback, user, try_edit=True, cities=cities)
            return
        data: dict = SERVICES_CHANNELS.get(city.name_pl, {})
        value = data.get(key)
        
        if value is None:
            # такой услуги в этом городе нету
            await service_not_availabel(callback, user, city_id=city_id, try_edit=True)
        else:
            if isinstance(value, int):
                # значит айди канала. продолжаем ввод 
                if key == "moving_transport":
                    # если выбор помощь для переезда то выдаем сообщение с кнопкой продолжить
                    new_message = await send_wait_start_address_service(callback, user, city_id=city_id, try_edit=True)
                    name_uk = btn("uk", key=key)
                    await state.set_state(ServiceStates.wait_start_address)
                    await state.set_data({
                        "to_delete": [
                            (new_message.chat.id, new_message.message_id)
                            ],
                        "channel_id": value,
                        "key": key,
                        "city": city.name_uk,
                        "city_id": city_id,
                        "work_type": name_uk})

            else:
                await callback.answer()

    elif command == "finish":
        # нажата кнопка опубликовать без контакта и комментария
        old_data = await state.get_data()
        await state.clear()
        await process_service_request(session, callback, user, old_data, try_edit=True)

@router.message(StateFilter(ServiceStates.wait_start_address))
async def handle_start_address(message: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    ожидаем от юзера адрес откуда переезжать
    """
    start_address = message.text or message.caption
    await message.delete()
    if start_address is None:
        return
    
    old_data = await state.get_data()
    if not old_data:
        cities = await get_cities(session, CITIES_STR)
        await builders_services(message, user, try_edit=False, cities=cities)
        return
    if old_data:
        items = old_data.pop("to_delete", [])
        for ch_id, m_id in items:
            try:
                await message.bot.delete_message(ch_id, m_id)
            except Exception as e:
                pass
    city_id = old_data["city_id"]

    new_message = await send_wait_end_address_service(message, user, city_id=city_id, try_edit=False)
    old_data["start_address"] = start_address
    old_data["to_delete"] = [(new_message.chat.id, new_message.message_id)]
    
    await state.set_state(ServiceStates.wait_end_address)
    await state.set_data(old_data)


@router.message(StateFilter(ServiceStates.wait_end_address))
async def handle_end_address(message: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    ожидаем от юзера адрес куда перезжать
    """
    end_address = message.text or message.caption
    await message.delete()
    if end_address is None:
        return
    
    old_data = await state.get_data()
    if not old_data:
        cities = await get_cities(session, CITIES_STR)
        await builders_services(message, user, try_edit=False, cities=cities)
        return
    if old_data:
        items = old_data.pop("to_delete", [])
        for ch_id, m_id in items:
            try:
                await message.bot.delete_message(ch_id, m_id)
            except Exception as e:
                pass
    city_id = old_data["city_id"]

    new_message = await send_wait_description_service(message, user, city_id=city_id, try_edit=False)
    old_data["end_address"] = end_address
    old_data["to_delete"] = [(new_message.chat.id, new_message.message_id)]
    
    await state.set_state(ServiceStates.wait_description)
    await state.set_data(old_data)


@router.message(StateFilter(ServiceStates.wait_description))
async def handle_description(message: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    ожидаем что юзер пишет номер телефона и дополнительные данные для заявки
    {
        "channel_id": -1003336596169,
        "key": "moving_transport",
        "city": "Краків",
        "city_id": 65,
        "work_type": "🚚 Транспорт при переїзді",
        "start_address": "Варшава",
        "end_address": "Катовице",
        "description": description
    }
    """
    description = message.text or message.caption
    await message.delete()
    if description is None:
        return
    
    old_data: dict = await state.get_data()

    if not old_data:
        cities = await get_cities(session, CITIES_STR)
        await builders_services(message, user, try_edit=False, cities=cities)
        return
    
    if old_data:
        items = old_data.pop("to_delete", [])
        for ch_id, m_id in items:
            try:
                await message.bot.delete_message(ch_id, m_id)
            except Exception as e:
                pass
    old_data["description"] = description
    await state.clear()

    await process_service_request(session, message, user, old_data, try_edit=False)
    


async def process_service_request(
        session: AsyncSession,
        target: Message | CallbackQuery,
        user: User,
        data: dict,
        try_edit: bool=False) -> Message:
    '''
    создаем сообщение в очередь на отправку в канал
    также записываем статистику по заявкам
    data = {
            "channel_id": -1003336596169,
            "key": "moving_transport",
            "city": "Краків",
            "city_id": 65,
            "work_type": "🚚 Транспорт при переїзді",
            "start_address": "Варшава",
            "end_address": "Катовице",
            "description": description
        }
    text =📍 Місто: {{city}}
🛠 Вид робіт: {{work_type}}
💬 Мова спілкування: {{language}}
👤 Користувач: @{{username}}
📞 Статус: очікує дзвінка від асистента"
    '''
    text = f"📍 Місто: {data.get('city')}\n"
    text += f"🛠 Вид робіт: {data.get('work_type')}\n"
    text += f"📍Звідки: {data.get('start_address')}\n" if data.get('start_address') else ''
    text += f"📍Куди: {data.get('end_address')}\n" if data.get('end_address') else ''
    text += f"💬 Мова спілкування: {user.language}\n"
    text += f"👤 Користувач: {user.get_link}\n"
    text += f"📞 Статус: очікує дзвінка від асистента\n"
    text += f"📝 Контакт та коментарі:\n{escape(data.get('description', '-----'))}\n"
        
    await schedule_message(
            session,
            MessageType.CUSTOM,
            chat_type=ChatType.CHANNEL,
            chat_id=data.get("channel_id"),
            
            payload={"from": "service", "text": text},
            user_id=user.id
            )
    await add_statistic_data(session, user, "services", "send", data)

    return await your_request_was_accepted_service(target, user, try_edit)
    


@router.callback_query(F.data.startswith("select_city_agent|"))
async def select_city_agent_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    '''
    выбор города для других услуг.
    select_city_agent|select_city_agent кнопка назад
    select_city_agent|city|{city_id} кнопка выдор города
    select_city_agent|keys|rent or sale|{city_id} кнопка выбор услуги в городе
    select_city_agent|confirm|rent or sale|{city_id}
    '''
    _, command = callback.data.split("|", 1)  # city|122

    if command == "select_city_agent":
        # назад к выбору города
        cities = await get_cities(session, CITIES_STR)
        await contact_agent(callback, user, try_edit=True, cities=cities)

    elif command.startswith("city|"):
        # выьран город, переходим к выбору услуги
        _, city_id = command.split("|", 1)  # 124
        # --- получить или создать фильтр для пользователя ---
        city_id = int(city_id)
        city = await session.get(City, city_id)
        if not city:
            # если города нету то возвращаем к выбору городов
            cities = await get_cities(session, CITIES_STR)
            await contact_agent(callback, user, try_edit=True, cities=cities)
            return
        await agent_deal_type(callback, user, int(city_id), True)
        await state.clear()
    
    elif command.startswith("keys|"):
        # выьран город, переходим к выбору услуги
        _, deal_type, city_id = command.split("|", 2)  # rent or sale, 124
        # --- получить или создать фильтр для пользователя ---
        city_id = int(city_id)
        city = await session.get(City, city_id)
        if not city:
            # если города нету то возвращаем к выбору городов
            cities = await get_cities(session, CITIES_STR)
            await contact_agent(callback, user, try_edit=True, cities=cities)
            return
        
        new_message = await agent_price_range(callback, user, city_id, True)

        await state.set_state(AgentStates.wait_price_range)
        await state.set_data({
            "to_delete": [
                (new_message.chat.id, new_message.message_id)
                ],
            "key": "agent",
            "deal_type": deal_type,
            "city": city.name_uk,
            "city_id": city_id,
            })