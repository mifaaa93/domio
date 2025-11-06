from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.texts import btn
from db.models import User, Listing
from bot.utils.helpers import add_query_params
from config import MINIAPP_URL


def get_under_listing_btns(listing: Listing, user: User, saved_ids: list[int]=[]) -> InlineKeyboardMarkup:
    """просмотра результатов"""
    builder = InlineKeyboardBuilder()
    # кнопка со ссылкой на квартиру
    
    # кнопка карта
    if listing.map_url:
        builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "map_btn"), url=listing.map_url)
        )
    if listing.id in saved_ids:
        # если листинг в сохраненных
        builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "unlike_listing_btn"),
                callback_data=f"listing|unlike|{listing.id}")
        )
    else:
        # если листинг не в сохраненных
        builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "like_listing_btn"),
                callback_data=f"listing|like|{listing.id}")
        )
    builder.adjust(2)
    
    builder.row(
        InlineKeyboardButton(text=btn(user.language_code, "open_listing_btn"), url=listing.url)
    )
    # кнопка в миниапп
    params = {
        "type": "listing",
        "lang": user.language_code,
        }
    url = add_query_params(MINIAPP_URL, params)
    builder.row(
        InlineKeyboardButton(text=btn(user.language_code, "show_all_btn"), web_app=WebAppInfo(url=url))
    )

    return builder.as_markup()