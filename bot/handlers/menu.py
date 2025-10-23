# bot\handlers\menu.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from bot.utils.messages import *
from bot.texts import btn_tuple

router = Router()


@router.message(F.text.in_(btn_tuple("search")))
async def search_btn_press(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    нажата кнопка поиск квартир
    """
    if user.language_code is None:
        await send_language_prompt(msg)
        return

    # передаем в search-цепочку (первая стадия выбора типа пошуку)
    await start_search(msg, user)