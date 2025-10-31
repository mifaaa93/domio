from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.texts import btn
from db.models import User, Listing


def get_under_listing_btns(listing: Listing, user: User) -> InlineKeyboardMarkup:
    """просмотра результатов"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=btn(user.language_code, "open_listing_btn"), url=listing.url)
    )
    builder.row(
        InlineKeyboardButton(text=btn(user.language_code, "open_listing_btn"), url=listing.url)
    )

    return builder.as_markup()