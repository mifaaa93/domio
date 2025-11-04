from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.texts import btn
from bot.utils.helpers import add_query_params
from config import REGLAMENT_URLS, PRIVACI_URLS, CREATE_INVOICE_URL


def subscribe_main_keyboard(lang: str='uk', show_reglament: bool=True) -> InlineKeyboardMarkup:
    """клавиатура выбора тарифов оплаты"""
    subs_names = ("test", "2week", "month",)
    builder = InlineKeyboardBuilder()

    for name in subs_names:
        builder.row(
        InlineKeyboardButton(
            text=btn(lang, f"subscribe_main_{name}_btn"),
            web_app=WebAppInfo(url=add_query_params(
                CREATE_INVOICE_URL,
                {
                    "subscribe_type": name,
                    "invoice_type": "SUBSCRIPTION",
                    "lang": lang,}))))
    
    if show_reglament:
        # Кнопка "регламент" отдельной строкой
        builder.row(
            InlineKeyboardButton(
                text=btn(lang, "reglament_btn_text"),
                web_app=WebAppInfo(url=REGLAMENT_URLS.get(lang, REGLAMENT_URLS.get("pl")))),
            InlineKeyboardButton(
                text=btn(lang, "privacy_btn_text"),
                web_app=WebAppInfo(url=PRIVACI_URLS.get(lang, PRIVACI_URLS.get("pl"))))
        )
    
    return builder.as_markup()



def pay_btn_keyboard(url: str, amount: float, lang: str='uk', show_reglament: bool=True) -> InlineKeyboardMarkup:
    """клавиатура выбора тарифов оплаты"""
    builder = InlineKeyboardBuilder()

    # кнопка любой площади
    builder.row(
        InlineKeyboardButton(
            text=btn(lang, "pay_btn").format(amount=amount),
            url=url)
    )

    if show_reglament:# Кнопка "регламент" отдельной строкой
        builder.row(
            InlineKeyboardButton(
                text=btn(lang, "reglament_btn_text"),
                web_app=WebAppInfo(url=REGLAMENT_URLS.get(lang, REGLAMENT_URLS.get("pl")))),
            InlineKeyboardButton(
                text=btn(lang, "privacy_btn_text"),
                web_app=WebAppInfo(url=PRIVACI_URLS.get(lang, PRIVACI_URLS.get("pl"))))
        )
    
    return builder.as_markup()