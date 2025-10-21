from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка: 🇺🇦 Українська / 🇬🇧 English / 🇵🇱 Polski
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            ],
            [
                InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl"),
            ],
            [
                InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
            ],
        ]
    )
