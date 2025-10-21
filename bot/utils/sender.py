import os
import logging
from typing import Optional, Union
from aiogram.types import (
    Message, CallbackQuery, FSInputFile, InputMediaPhoto,
    InputMediaVideo, InputMediaDocument, InputMediaAnimation
)
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot

from bot.utils.images import get_image

logger = logging.getLogger("bot")

# --- Глобальный кеш медиа file_id ---
_media_cache: dict[tuple[str, str, str], str] = {}
# (lang, key, type) → file_id


async def send_or_edit_message(
    target: Union[Message, CallbackQuery],
    *,
    key: str,
    lang: Optional[str] = None,
    text: Optional[str] = None,
    keyboard=None,
    bot: Optional[Bot] = None,
    try_edit: bool = False,
    media_type: str = "photo",   # photo | video | document | animation
    use_assets: bool = True,     # брать файл из assets
) -> Message:
    """
    Универсальная функция для отправки/редактирования сообщений с кешом file_id.
    """

    # --- определяем контекст ---
    msg = target.message if isinstance(target, CallbackQuery) else target
    chat_id = msg.chat.id
    lang = lang or "uk"
    bot = bot or msg.bot

    # --- готовим текст и клавиатуру ---
    caption = text or ""
    reply_markup = keyboard

    # --- ищем медиа (если нужно) ---
    file_id = None
    media_file = None
    cache_key = (lang, key, media_type)

    if use_assets:
        file_id = _media_cache.get(cache_key)
        if not file_id:
            media_file = get_image(lang, key) if media_type == "photo" else None

    # --- попытка редактирования ---
    if try_edit:
        try:
            if media_file or file_id:
                media_cls = {
                    "photo": InputMediaPhoto,
                    "video": InputMediaVideo,
                    "document": InputMediaDocument,
                    "animation": InputMediaAnimation,
                }.get(media_type, InputMediaPhoto)

                media = media_cls(
                    media=file_id or media_file,
                    caption=caption,
                )
                await msg.edit_media(media=media, reply_markup=reply_markup)
            else:
                await msg.edit_text(caption, reply_markup=reply_markup)
            return msg
        except TelegramBadRequest as e:
            # если редактирование не удалось — удаляем и отправляем новое
            logger.debug(f"Edit failed for key={key}: {e}")
            try:
                await msg.delete()
            except TelegramBadRequest:
                pass

    # --- отправляем новое сообщение ---
    sent: Message | None = None

    try:
        if media_file or file_id:
            # Отправляем медиа
            sender = {
                "photo": bot.send_photo,
                "video": bot.send_video,
                "document": bot.send_document,
                "animation": bot.send_animation,
            }.get(media_type, bot.send_photo)

            sent = await sender(
                chat_id=chat_id,
                photo=file_id or media_file,
                caption=caption,
                reply_markup=reply_markup,
            ) if media_type == "photo" else await sender(
                chat_id=chat_id,
                caption=caption,
                reply_markup=reply_markup,
                video=file_id or media_file if media_type == "video" else None,
                document=file_id or media_file if media_type == "document" else None,
                animation=file_id or media_file if media_type == "animation" else None,
            )

            # --- кешируем новый file_id ---
            if sent and hasattr(sent, "photo") and sent.photo:
                _media_cache[cache_key] = sent.photo[-1].file_id
            elif sent and hasattr(sent, media_type):
                fobj = getattr(sent, media_type, None)
                if fobj and hasattr(fobj, "file_id"):
                    _media_cache[cache_key] = fobj.file_id

        else:
            sent = await bot.send_message(chat_id=chat_id, text=caption, reply_markup=reply_markup)

    except TelegramBadRequest as e:
        # если file_id стал невалидным → очистим кеш
        if "file not found" in str(e).lower():
            _media_cache.pop(cache_key, None)
            logger.warning(f"Invalid file_id, cache cleared for {cache_key}")
            # повторим попытку без кеша
            return await send_or_edit_message(
                target,
                key=key,
                lang=lang,
                text=text,
                keyboard=keyboard,
                bot=bot,
                try_edit=False,
                media_type=media_type,
                use_assets=True,
            )
        else:
            raise

    return sent
