from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from config import LANGUAGES

from db.models import User
from db.repo_async import get_user_by_token
from bot.utils.messages import *

router = Router()

@router.my_chat_member()
async def block_unblock_bot(chat_member: ChatMemberUpdated, session: AsyncSession):
    '''
    юзер блокирует бота
    '''
    if not chat_member.from_user:
        return  # Нет данных о пользователе — пропускаем
    status = chat_member.new_chat_member.status
    new_status = status not in ("left", "kicked")
    user = await get_user_by_token(session, chat_member.from_user.id)
    if user is None:
        return
    if user.is_active != new_status:
        user.is_active = new_status
        await session.commit()


@router.message(CommandStart())
async def start_cmd(msg: Message, command: CommandObject, session: AsyncSession, user: User, state: FSMContext):
    """
    Стартовый хендлер:
    - если язык не выбран → показать выбор языка
    - иначе — приветствие
    """
    raw = command.args
    if raw and raw in LANGUAGES:
        # если по ссылке с сайта
        user.language_code = raw
        await session.commit()
        await send_main_menu(msg, user)
        await trigger_invoice(msg, user)
    elif user.language_code is None:
        await send_language_prompt(msg, user)
    else:
        await send_main_menu(msg, user)
    await state.clear()


@router.callback_query(F.data == "main_menu")
async def goto_main_menu(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    await send_main_menu(callback, user, try_edit=True)
    await state.clear()