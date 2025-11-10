from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.texts import btn
from db.models import User



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
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_rent_btn"), callback_data="how_to_use|instruction_rent"))
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_buy_btn"), callback_data="how_to_use|instruction_buy"))
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_mortgage_btn"), callback_data="how_to_use|instruction_mortgage"))
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_access_btn"), callback_data="how_to_use|instruction_access"))
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_services_btn"), callback_data="how_to_use|instruction_services"))
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_earn_btn"), callback_data="how_to_use|instruction_earn"))
    return builder.as_markup()


def how_to_use_prime_sec_btns(user: User) -> InlineKeyboardMarkup:
    """кнопки инструкций для подменю покупка (новострой или бу)"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_primary_btn"), callback_data="how_to_use|instruction_primary"))
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "instruction_secondary_btn"), callback_data="how_to_use|instruction_secondary"))
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "back"), callback_data="how_to_use|how_to_use"))
    return builder.as_markup()

def back_to_how_to_use_btns(user: User) -> InlineKeyboardMarkup:
    """кнопки инструкций для подменю покупка (новострой или бу)"""
    builder = InlineKeyboardBuilder()
    # кнопка отключения автопродления
    builder.row(
            InlineKeyboardButton(text=btn(user.language_code, "back"), callback_data="how_to_use|how_to_use"))
    return builder.as_markup()