from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from bot.states import LanguageStates
from bot.keyboards.lang import get_language_keyboard
from bot.texts import t

router = Router()


@router.message(F.text == "/menu")
async def start_cmd(msg: Message, session: AsyncSession, user: User, state: FSMContext):
    if user.language_code is None:
        await msg.answer(t(None, "choose_language"), reply_markup=get_language_keyboard())
        await state.set_state(LanguageStates.choosing)
        return

    await msg.answer(t(user.language_code, "greeting"))


@router.callback_query(F.data.startswith("lang_"))
async def choose_language(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    lang_code = callback.data.split("_", 1)[1]
    user.language_code = lang_code
    session.add(user)
    await session.commit()

    await callback.message.edit_text(t(lang_code, "language_set"))
    await state.clear()
