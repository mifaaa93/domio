from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.texts import btn
from db.models import User



def get_settings_keyboard(user: User) -> InlineKeyboardMarkup:
    """кнопки меню настроек"""
    builder = InlineKeyboardBuilder()
    # кнопка выбора языка
    builder.row(
        InlineKeyboardButton(
            text=btn(user.language_code, "language"),
            callback_data="settings|language")
    )
    if user.recurring_on:
        builder.row(
            InlineKeyboardButton(
                text=btn(user.language_code, "recurring"),
                callback_data="settings|recurring")
        )
    return builder.as_markup()


def recurring_prompt_disable(user: User) -> InlineKeyboardMarkup:
    """кнопки меню настроек"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления
    builder.row(
        InlineKeyboardButton(
            text=btn(user.language_code, "yes_btn"),
            callback_data="recurring|off")
    )

    builder.row(
        InlineKeyboardButton(
            text=btn(user.language_code, "back"),
            callback_data="settings|settings")
    )
    return builder.as_markup()