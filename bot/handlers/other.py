from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from config import REFERAL_CHANNEL

from db.models import User, MessageType, ChatType
from db.repo_async import schedule_message
from bot.utils.messages import *
from bot.texts import alert_t


router = Router()


@router.callback_query(F.data.startswith("earn|"))
async def earn_main_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, submenu = callback.data.split("|", 1)
    
    if submenu == "instruction":
        # инструкция по реферальной программе
        await earn_instruction(callback, user, True)
    
    elif submenu == "pay_out":
        # запрос подтверждения вывода средств
        if not user.referral_balance_current:
            await callback.answer(
                text=alert_t(user.language_code, "no_ref_balance"),
                show_alert=True
            )
        else:
            await ask_earn_payout(callback, user, True)
    
    elif submenu == "confirm_earn":
        # подтвердить списание
        # запрос подтверждения вывода средств
        if not user.referral_balance_current:
            await callback.answer(
                text=alert_t(user.language_code, "no_ref_balance"),
                show_alert=True
            )
            await earn_with_domio(callback, user, True)
        else:
            # средства есть, делаем запрос на вывод
            current = user.referral_balance_current
            user.referral_balance_current = 0.0
            await session.commit()
            await schedule_message(
                    session,
                    MessageType.CUSTOM,
                    chat_type=ChatType.CHANNEL,
                    chat_id=REFERAL_CHANNEL,
                    payload={"from": "confirm_earn", "amount": current},
                    user_id=user.id
                    )
            await payout_request_sended(callback, user, current, True)

    elif submenu == "earn":
        # кнопка назад в реферальное меню
        await earn_with_domio(callback, user, True)


@router.callback_query(F.data.startswith("how_to_use|"))
async def how_to_use_callback(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    
    _, submenu = callback.data.split("|", 1)
    
    if submenu == "how_to_use":
        # кнопка назад в реферальное меню
        await how_to_use(callback, user, True)
    
    elif submenu == "instruction_buy":
        # показываем подменю выбора инструкции
        btns = how_to_use_prime_sec_btns(user)
        await edit_btns(callback, btns)
    else:
        # тут инструкция по каждому пункуту
        await send_video_instruction(callback, user, True, submenu)

