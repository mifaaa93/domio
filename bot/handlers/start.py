from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from bot.utils.messages import *

router = Router()


@router.message(F.text == "/start")
async def start_cmd(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    """
    Стартовый хендлер:
    - если язык не выбран → показать выбор языка
    - иначе — приветствие
    """
    if user.language_code is None:
        await send_language_prompt(msg, user)
    else:
        await send_main_menu(msg, user)


@router.callback_query(F.data.startswith("lang_"))
async def choose_language(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    lang_code = callback.data.split("_", 1)[1]
    prew_code = user.language_code
    user.language_code = lang_code
    session.add(user)
    await session.commit()
    
    await send_language_set(callback, user)
    if prew_code is None:
        await send_main_menu(callback, user)



@router.callback_query(F.data == "main_menu")
async def goto_main_menu(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    await send_main_menu(callback, user, try_edit=True)