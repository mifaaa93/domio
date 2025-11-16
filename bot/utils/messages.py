from bot.utils.sender import send_or_edit_message, edit_btns
from bot.utils.images import get_image
from bot.texts import t, vid, guid, contact_key
from bot.keyboards.lang import get_language_keyboard
from bot.keyboards.menu import *
from bot.keyboards.subs import *
from bot.keyboards.other_kb import *
from bot.keyboards.settings import *
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from db.models import User, District, City, UserSearch
from config import BOT_URL, SUPPORT_USERNAME, REVIEWS_URL
from bot.utils.helpers import add_query_params


async def send_language_prompt(target: Message | CallbackQuery, user: User, try_edit: bool=False) -> Message:
    lang = user.language_code
    key = "choose_language"
    return await send_or_edit_message(
        target,
        key="choose_language",
        lang=lang,
        text=t(lang, key),
        keyboard=get_language_keyboard(user),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def send_language_set(target: Message | CallbackQuery, user: User, try_edit: bool=True) -> Message:
    lang = user.language_code
    key = "language_set"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def send_recurring_prompt(target: Message | CallbackQuery, user: User, try_edit: bool=True) -> Message:
    lang = user.language_code
    key = "recurring_prompt_disable"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=recurring_prompt_disable(user),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def send_main_menu(target: Message | CallbackQuery, user: User, try_edit: bool=False) -> Message:
    lang = user.language_code
    key = "main_menu"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_main_menu(user),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def start_search(target: Message | CallbackQuery, user: User, try_edit: bool=False) -> Message:
    """
    Обери тип пошуку
    """
    lang = user.language_code
    key = "search_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_search_type_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def comissiom_type(target: Message | CallbackQuery, user: User, try_edit: bool=True) -> Message:
    """
    Обери тип ринку
    """
    lang = user.language_code
    key = "comissiom_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_comissiom_type_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def estate_type(target: Message | CallbackQuery, user: User, try_edit: bool=True, deal_type: str='rent') -> Message:
    """
    Обери тип нерухомості
    """
    lang = user.language_code
    key = "estate_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_estate_type_keyboard(lang, deal_type),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def market_type(target: Message | CallbackQuery, user: User, try_edit: bool=True) -> Message:
    """
    Обери тип ринку
    """
    lang = user.language_code
    key = "market_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_market_type_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def select_city(target: Message | CallbackQuery, user: User, try_edit: bool=True, cities: list=[City]) -> Message:
    '''
    выбор города
    '''
    lang = user.language_code
    key = "select_city"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_select_city_keyboard(lang, cities),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def select_district(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True,
        all_districts: list[District]=[],
        selected_districts:  list[District]=[],
        only_btns: bool=False) -> Message:
    '''
    выбор райнов
    '''
    lang = user.language_code
    key = "select_district"
    if only_btns:
        try:
            return await edit_btns(target, keyboard=get_select_district_keyboard(lang, all_districts, selected_districts))
        except Exception as e:
            pass
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_select_district_keyboard(lang, all_districts, selected_districts),
        try_edit=try_edit,
        photo=get_image(lang, key),

    )


async def area_from(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True) -> Message:
    '''
    '''
    lang = user.language_code
    key = "area_from"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_area_from_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def area_to(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True,
        min_area: int=0) -> Message:
    '''
    '''
    lang = user.language_code
    key = "area_to"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_area_to_keyboard(lang, min_area or 0),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def rooms_count(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True,
        selected: list[int] = [],
        only_btns: bool=False) -> Message:
    '''
    '''
    lang = user.language_code
    key = "rooms_count"
    if only_btns:
        try:
            return await edit_btns(target, keyboard=get_rooms_count_keyboard(lang, selected))
        except Exception as e:
            pass
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_rooms_count_keyboard(lang, selected),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def min_price(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True) -> Message:
    '''
    ввод минимального бюджета
    '''
    lang = user.language_code
    key = "price_from"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_min_price_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def max_price(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True) -> Message:
    '''
    ввод максимального бюджета
    '''
    lang = user.language_code
    key = "price_to"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_max_price_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )



async def child(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True) -> Message:
    '''
    выбор наличия детей
    '''
    lang = user.language_code
    key = "child"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_child_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def pets(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True) -> Message:
    '''
    сообщения выбора животных
    '''
    lang = user.language_code
    key = "pets"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_pets_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def show_results(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=True,
        total: int=0,
        search: UserSearch= None) -> Message:
    '''
    сообщения выбора животных
    '''
    lang = user.language_code
    key = "results"
    search_str = search.get_str(lang)
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key).format(total=total, search=search_str),
        keyboard=get_results_keyboard(lang, search.id),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def trigger_invoice(
        target: Message | CallbackQuery=None,
        user: User=None,
        bot: Bot=None,
        try_edit: bool=False) -> Message:
    '''
    '''
    lang = user.language_code
    key = "subscribe_main"
    return await send_or_edit_message(
        target,
        bot=bot,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=subscribe_main_keyboard(lang),
        try_edit=try_edit,
        photo=get_image(lang, key),
        chat_id=user.id
    )


async def favorites(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False,
        total: int=0) -> Message:
    '''
    сообщения выбора животных
    '''
    lang = user.language_code
    key = "favorites"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key).format(total=total),
        keyboard=get_favorites_keyboard(lang) if total else None,
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def successful_subscription(
        target: Message | CallbackQuery=None,
        user: User=None,
        bot: Bot=None,
        try_edit: bool=False,
        payload: dict=None) -> Message:
    '''
    '''
    lang = user.language_code
    key = "successful_subscription"
    payload = payload or {}
    days = payload.get("days", "---")
    valid_to = user.subscription_until_str
    return await send_or_edit_message(
        target,
        bot=bot,
        key=key,
        lang=lang,
        text=t(lang, key).format(days=days, valid_to=valid_to),
        try_edit=try_edit,
        photo=get_image(lang, key),
        chat_id=user.id
    )


async def successful_subscription_channel(
        user: User=None,
        bot: Bot=None,
        payload: dict=None,
        chat_id: int=None) -> Message:
    '''
    инфо в канал когда подписка активирована
    '''
    payload = payload or {}
    days = payload.get("days", "---")
    valid_to = user.subscription_until_str
    user_link = user.get_link if user else "----"
    text = f"У {user_link} активована підписка на {days} дні(-ів)\n\nАктивна до: <b>{valid_to}</b>"
    return await bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=True
    )

async def successful_guides_channel(
        user: User=None,
        bot: Bot=None,
        payload: dict=None,
        chat_id: int=None) -> Message:
    '''
    инфо в канал когда подписка активирована
    '''
    user_link = user.get_link if user else "----"
    text = f"{user_link} придбав Гайд з купівлі нерухомості "
    return await bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=True
    )

async def successful_confirm_earn_channel(
        user: User=None,
        bot: Bot=None,
        payload: dict=None,
        chat_id: int=None) -> Message:
    '''
    инфо в канал когда подписка активирована
    '''
    payload = payload or {}
    amount = payload.get("amount", "---")
    user_link = user.get_link if user else "----"
    text = f"{user_link} запрошує вивід коштів за рефералів: <b>{amount} PLN</b>"
    return await bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=True
    )


async def successful_confirm_service_channel(
        user: User=None,
        bot: Bot=None,
        payload: dict=None,
        chat_id: int=None) -> Message:
    '''
    инфо в канал когда подписка активирована
    '''
    text = payload.get("text", str(payload))
    return await bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=True
    )

async def new_user_channel(
        user: User=None,
        bot: Bot=None,
        payload: dict=None,
        chat_id: int=None) -> Message:
    '''
    инфо в канал когда пришел новый юзер
    '''
    payload = payload or {}
    user_link = user.get_link if user else "----"
    text = f"Новий користувач: {user_link}"
    return await bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=True
    )

async def settings_main(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    сообщения настройки
    так же показываем инфо по подписке
    '''
    lang = user.language_code
    key = "settings"
    text = t(lang, key)
    if user.subscribed:
        if user.is_full_sub:
            text = t(lang, "sub_settings_full").format(until=user.subscription_until_str)
        else:
            text = t(lang, "sub_settings").format(until=user.subscription_until_str)
        if user.recurring_on:
            text += "\n\n" + t(lang, "autocontinue_info").format(date=user.autocontinue_str)
    else:
        text = t(lang, "no_sub_settings")

    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=text,
        keyboard=get_settings_keyboard(user),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def earn_with_domio(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    реферальное меню
    '''
    lang = user.language_code
    key = "earn_with_domio"
    url = add_query_params(BOT_URL, {"start": user.id})
    text = t(lang, key).format(
        url=url,
        current=user.referral_balance_current,
        total=user.referral_earnings_total)
    
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=text,
        keyboard=get_earn_with_domio_keyboard(user),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def help_message(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    помощь
    '''
    lang = user.language_code
    key = "support"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key).format(username=SUPPORT_USERNAME),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def reviews(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    отзывы
    '''
    lang = user.language_code
    key = "reviews"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key).format(url=REVIEWS_URL),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )



async def earn_instruction(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    инструкция по рефералке
    '''
    lang = user.language_code
    key = "earn_instruction"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        keyboard=get_earn_instruction_keyboard(user),
        photo=get_image(lang, key)
    )


async def ask_earn_payout(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    запрос на вывод баланса
    '''
    lang = user.language_code
    key = "ask_earn_payout"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key).format(current=user.referral_balance_current),
        try_edit=try_edit,
        keyboard=earn_confirm_payout(user),
        photo=get_image(lang, key)
    )


async def payout_request_sended(
        target: Message | CallbackQuery,
        user: User,
        amount: float,
        try_edit: bool=False) -> Message:
    '''
    запрос на вывод баланса
    '''
    lang = user.language_code
    key = "payout_request_sended"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key).format(amount=amount),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def only_full_sub_message(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    отзывы
    '''
    lang = user.language_code
    key = "only_full_sub"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def how_to_use(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    меню выбора инструкции
    '''
    lang = user.language_code
    key = "how_to_use"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        keyboard=how_to_use_btns(user),
        photo=get_image(lang, key)
    )


async def send_video_instruction(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False,
        submenu: str=None) -> Message:
    '''
    сделать отправку видео по айди.
    пока что только отправка текста
    '''
    lang = user.language_code
    caption = t(lang, submenu)
    video_id = vid(lang, submenu)

    return await send_or_edit_message(
        target,
        key=submenu,
        lang=lang,
        text=caption,
        try_edit=try_edit,
        keyboard=back_to_how_to_use_btns(user),
        video_file_id=video_id
    )


async def guides(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    меню гайдов
    '''
    lang = user.language_code
    key = "guides"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        keyboard=guides_btns(user),
        photo=get_image(lang, key)
    )

async def guides_rent(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False) -> Message:
    '''
    файл гайдов по аренде
    '''
    lang = user.language_code
    key = "guides_rent"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        keyboard=guides_rent_btns(user),
        photo=get_image(lang, key)
    )

async def guides_sale(
        target: Message | CallbackQuery=None,
        user: User=None,
        try_edit: bool=False,
        bot: Bot=None) -> Message:
    '''
    файл гайдов по покупке
    '''
    lang = user.language_code
    key = "guides_sale"
    toc_link = guid(lang, key)
    return await send_or_edit_message(
        target,
        bot=bot,
        chat_id=user.id,
        key=key,
        lang=lang,
        text=t(lang, key).format(toc_link=toc_link),
        try_edit=try_edit,
        keyboard=guides_sale_btns(user),
        photo=get_image(lang, key)
    )

async def contact_agent(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False,
        cities: list=[City]
        ) -> Message:
    '''
    выбор города для риелтора
    '''
    lang = user.language_code
    key = "select_city_agent"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_select_city_keyboard(lang, cities, "select_city_agent|city", False),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def builders_services(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False,
        cities: list=[City]
        ) -> Message:
    '''
    выбор города для других услуг
    '''
    lang = user.language_code
    key = "select_city_builders"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_select_city_keyboard(lang, cities, "other|city", False),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )


async def builders_type(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        try_edit: bool=False,
        ) -> Message:
    '''
    выбор города для других услуг
    '''
    lang = user.language_code
    key = "builders_type"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_builders_type_keyboard(user, city_id),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def service_not_availabel(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        try_edit: bool=False,
        ) -> Message:
    '''
    выбор города для других услуг
    '''
    lang = user.language_code
    key = "service_not_availabel"
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=back_to_services_keyboard(user, city_id),
        try_edit=try_edit,
        photo=get_image(lang, key)
    )

async def send_contact_for_service(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        key: str,
        try_edit: bool=False,
        ) -> Message:
    '''
    показываем контакт сервиса и кнопка назад к выбору услуг
    '''
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=contact_key(lang, key),
        keyboard=back_to_services_keyboard(user, city_id),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )


async def moving_transport_first(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        key: str,
        try_edit: bool=False,
        ) -> Message:
    '''
    показываем контакт сервиса и кнопка назад к выбору услуг
    '''
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=back_to_services_or_continu_keyboard(user, city_id, key),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )

async def send_wait_description_service(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        try_edit: bool=False,
        ) -> Message:
    '''
    показываем контакт сервиса и кнопка назад к выбору услуг
    '''
    key = "wait_description_service"
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=cancel_or_confirm_services_keyboard(user, city_id),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )


async def send_wait_start_address_service(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        try_edit: bool=False,
        ) -> Message:
    '''
    показываем контакт сервиса и кнопка назад к выбору услуг
    '''
    key = "wait_start_address_service"
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=back_to_services_keyboard(user, city_id),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )

async def send_wait_end_address_service(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        try_edit: bool=False,
        ) -> Message:
    '''
    показываем контакт сервиса и кнопка назад к выбору услуг
    '''
    key = "wait_end_address_service"
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=back_to_services_keyboard(user, city_id),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )


async def your_request_was_accepted_service(
        target: Message | CallbackQuery,
        user: User,
        try_edit: bool=False,
        ) -> Message:
    '''
    уведомление что заявка принята
    '''
    key = "request_was_accepted"
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )


async def agent_deal_type(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        try_edit: bool=False,
        ) -> Message:
    '''
    показываем контакт сервиса и кнопка назад к выбору услуг
    '''
    key = "search_type"
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=get_deal_type_agent_btn(user, city_id),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )

async def agent_price_range(
        target: Message | CallbackQuery,
        user: User,
        city_id: int,
        try_edit: bool=False,
        ) -> Message:
    '''
    показываем контакт сервиса и кнопка назад к выбору услуг
    '''
    key = "price_range"
    lang = user.language_code
    return await send_or_edit_message(
        target,
        key=key,
        lang=lang,
        text=t(lang, key),
        keyboard=back_to_select_deal_type_agent_keyboard(user, city_id),
        try_edit=try_edit,
        #photo=get_image(lang, key)
    )