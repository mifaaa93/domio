from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.texts import btn, guid
from db.models import User
from bot.utils.helpers import add_query_params
from config import REGLAMENT_URLS, PRIVACI_URLS, CREATE_INVOICE_URL




def get_earn_with_domio_keyboard(user: User) -> InlineKeyboardMarkup:
    """кнопки меню настроек"""
    builder = InlineKeyboardBuilder()
    # кнопка выбора языка
    builder.row(
        InlineKeyboardButton(
            text=btn(user.language_code, "instruction_btn"),
            callback_data="earn|instruction")
    )
    if user.referral_balance_current:
        builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "pay_out_btn"),
                callback_data="earn|pay_out")
        )
    return builder.as_markup()


def earn_confirm_payout(user: User) -> InlineKeyboardMarkup:
    """кнопки подтвердить списание баланса"""
    builder = InlineKeyboardBuilder()
    
    # кнопка отключения автопродления
    if user.referral_balance_current:
        builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "yes_btn"),
                callback_data="earn|confirm_earn")
        )

    builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data="earn|earn")
        )
    return builder.as_markup()



def get_earn_instruction_keyboard(user: User) -> InlineKeyboardMarkup:
    """кнопки подтвердить списание баланса"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления
    builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data="earn|earn")
        )
    return builder.as_markup()

def how_to_use_btns(user: User) -> InlineKeyboardMarkup:
    """кнопки инструкций"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления
    builder.row(InlineKeyboardButton(text=btn(user.language_code, "instruction_rent_btn"), callback_data="how_to_use|instruction_rent"))
    builder.row(InlineKeyboardButton(text=btn(user.language_code, "instruction_buy_btn"), callback_data="how_to_use|instruction_sale"))
    return builder.as_markup()


def back_to_how_to_use_btns(user: User) -> InlineKeyboardMarkup:
    """кнопки инструкций для подменю покупка (новострой или бу)"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "back"), callback_data="how_to_use|how_to_use"))
    return builder.as_markup()



def guides_btns(user: User) -> InlineKeyboardMarkup:
    """кнопки гайдов"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления
    if user.language_code == "uk":
        builder.add(InlineKeyboardButton(
            text=btn(user.language_code, "guide_rent_btn"),
            callback_data="guides|rent"))
    
    builder.add(InlineKeyboardButton(
            text=btn(user.language_code, "guide_sale_btn"),
            callback_data="guides|sale"))
    
    builder.adjust(1)

    return builder.as_markup()


def guides_rent_btns(user: User) -> InlineKeyboardMarkup:
    """кнопки гайдов"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления       
    builder.add(
        InlineKeyboardButton(
            text=btn(user.language_code, "download"),
            url=guid(user.language_code, "rent")))
    builder.add(
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data="guides|guides"))
    
    builder.adjust(1)

    return builder.as_markup()


def guides_sale_btns(user: User, show_reglament: bool=True) -> InlineKeyboardMarkup:
    """кнопки гайда по покупке (оплата или файл)"""
    builder = InlineKeyboardBuilder()
    lang = user.language_code
    # кнопка отключения автопродления 
    if user.is_paid:      
        builder.row(
            InlineKeyboardButton(
                text=btn(lang, "download"),
                url=guid(lang, "sale")))
    else:
        # ставим кнопку на оплату
        builder.row(
            InlineKeyboardButton(
                text=btn(lang, "download"),
                web_app=WebAppInfo(url=add_query_params(
                CREATE_INVOICE_URL,
                {
                    "subscribe_type": "guides",
                    "invoice_type": "ONE_TIME",
                    "lang": lang,}))))
        
        if show_reglament:
            builder.row(
                InlineKeyboardButton(
                    text=btn(lang, "reglament_btn_text"),
                    web_app=WebAppInfo(url=REGLAMENT_URLS.get(lang, REGLAMENT_URLS.get("pl")))),
                InlineKeyboardButton(
                    text=btn(lang, "privacy_btn_text"),
                    web_app=WebAppInfo(url=PRIVACI_URLS.get(lang, PRIVACI_URLS.get("pl"))))
            )
        
    builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data="guides|guides"))
    

    return builder.as_markup()


def get_builders_type_keyboard(user: User, city_id: int) -> InlineKeyboardMarkup:
    """выбор других услуг"""
    builder = InlineKeyboardBuilder()
    lang = user.language_code
    # кнопка отключения автопродления 
    keys = (
        "repair_turnkey",
        "plumber",
        "custom_furniture",
        "electrician",
        "small_repairs",
        "notary",
        "sworn_translator",
        "moving_transport",
        "technical_acceptance",)
    for key in keys:
        if key == "sworn_translator" and lang == "pl":
            continue
        builder.add(
            InlineKeyboardButton(
                text=btn(lang, key),
                callback_data=f"other|keys|{key}|{city_id}"))
    
    builder.adjust(1)
    builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data="other|other"))
    

    return builder.as_markup()


def back_to_services_keyboard(user: User, city_id: int) -> InlineKeyboardMarkup:
    """кнопка назад когда сервис не доступен в этом городе"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления 
    
    builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data=f"other|city|{city_id}"))
    

    return builder.as_markup()


def back_to_services_or_continu_keyboard(user: User, city_id: int, key: str) -> InlineKeyboardMarkup:
    """кнопка назад когда сервис не доступен в этом городе"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления 
    builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "go"),
                callback_data=f"other|confirm|{key}|{city_id}"))
    builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data=f"other|city|{city_id}"))
    

    return builder.as_markup()


def cancel_or_confirm_services_keyboard(user: User, city_id: int) -> InlineKeyboardMarkup:
    """
    кнопки регламент и политика конфиденциальности
    кнопка отмены и кнопка пропустить
    """
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления 
    lang = user.language_code

    builder.row(
            InlineKeyboardButton(
                text=btn(lang, "skip"),
                callback_data=f"other|finish"))
    
    builder.row(
            InlineKeyboardButton(
                text=btn(lang, "cancel"),
                callback_data=f"other|city|{city_id}"))
    builder.row(
            InlineKeyboardButton(
                text=btn(lang, "reglament_btn_text"),
                web_app=WebAppInfo(url=REGLAMENT_URLS.get(lang, REGLAMENT_URLS.get("pl")))),
            InlineKeyboardButton(
                text=btn(lang, "privacy_btn_text"),
                web_app=WebAppInfo(url=PRIVACI_URLS.get(lang, PRIVACI_URLS.get("pl"))))
        )

    return builder.as_markup()