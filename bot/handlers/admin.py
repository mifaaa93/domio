# bot/handlers/search.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command, CommandObject

from db.models import User
from db.repo_async import *
from bot.texts import alert_t
from bot.utils.messages import *

from config import ADMIN_IDS

admin_menu_btns = (
    "Активувати ✅",
    "Дективувати ❌",
    "Статистика 📊",
)

def admin_menu_markup() -> ReplyKeyboardMarkup:

    markup = ReplyKeyboardBuilder()

    markup.add(*[KeyboardButton(text=name) for name in admin_menu_btns])
    markup.adjust(2)

    return markup.as_markup(resize_keyboard=True, one_time_keyboard=False)


router = Router()
# применяем глобальный фильтр — теперь ВСЕ message-хендлеры этого роутера будут проверять admin id
router.message.filter(F.from_user.id.in_(tuple(ADMIN_IDS)))
# и для callback_query (если у тебя есть callback handlers)
router.callback_query.filter(F.from_user.id.in_(tuple(ADMIN_IDS)))

@router.message(Command("admin"))
async def admin_cmd(msg: Message, command: CommandObject, session: AsyncSession, user: User, state: FSMContext):
    """
    админ меню
    """
    await msg.answer(
        text="Admin меню:",
        reply_markup=admin_menu_markup()
    )
