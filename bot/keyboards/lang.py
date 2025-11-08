from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models import User
from bot.texts import btn


def get_language_keyboard(user: User) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка: 🇺🇦 Українська / 🇬🇧 English / 🇵🇱 Polski
    """
    inline_keyboard=[
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang|en"),
            ],
            [
                InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang|pl"),
            ],
            [
                InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang|uk"),
            ],
        ]
    if user.language_code is not None:
        inline_keyboard.append([
            InlineKeyboardButton(
                text=btn(user.language_code, "back"),
                callback_data="settings|settings")
        ])
    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )
