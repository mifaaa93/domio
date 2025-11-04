from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.texts import btn
from db.models import User, Listing
from bot.utils.helpers import add_query_params
from config import MINIAPP_URL


def get_under_listing_btns(listing: Listing, user: User) -> InlineKeyboardMarkup:
    """просмотра результатов"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=btn(user.language_code, "open_listing_btn"), url=listing.url)
    )
    params = {
        "type": "listing",
        "lang": user.language_code,
        }
    url = add_query_params(MINIAPP_URL, params)
    builder.row(
        InlineKeyboardButton(text=btn(user.language_code, "show_all_btn"), web_app=WebAppInfo(url=url))
    )

    return builder.as_markup()