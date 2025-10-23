import logging
from typing import Optional, Union
from aiogram import Bot
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InlineKeyboardMarkup, ReplyKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAnimation,
)
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger("bot")

# --- Глобальный кеш file_id ---
# (lang, key, type) → file_id
_media_cache: dict[tuple[str, str, str], str] = {}


async def send_or_edit_message(
    target: Union[Message, CallbackQuery],
    *,
    key: str,
    lang: str = "uk",
    text: Optional[str] = None,
    keyboard: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None,
    bot: Optional[Bot] = None,
    try_edit: bool = False,
    photo: Optional[str] = None,
    video: Optional[str] = None,
    document: Optional[str] = None,
    animation: Optional[str] = None,
) -> Message:
    """
    Универсальная функция для отправки/редактирования сообщений Telegram.
    ✅ принимает путь до файла (photo/video/document/animation)
    ✅ использует кеш file_id (по ключу (lang, key, media_type))
    ✅ поддерживает try_edit (edit_media/edit_text)
    ✅ автоматически определяет тип клавиатуры (inline/reply)
    """

    # --- контекст ---
    msg = target.message if isinstance(target, CallbackQuery) else target
    chat_id = msg.chat.id
    bot = bot or msg.bot
    caption = text or ""

    # --- определяем тип медиа и путь ---
    media_type = None
    media_path = None
    if photo:
        media_type, media_path = "photo", photo
    elif video:
        media_type, media_path = "video", video
    elif document:
        media_type, media_path = "document", document
    elif animation:
        media_type, media_path = "animation", animation

    cache_key = (lang, key, media_type or "text")
    file_id = _media_cache.get(cache_key)
    media_file = None if file_id else (FSInputFile(media_path) if media_path else None)

    # --- редактирование ---
    if try_edit:
        try:
            # ⚙️ если меняется тип клавиатуры — не редактируем
            if msg.reply_markup and keyboard:
                old_is_inline = isinstance(msg.reply_markup, InlineKeyboardMarkup)
                new_is_inline = isinstance(keyboard, InlineKeyboardMarkup)
                if old_is_inline != new_is_inline:
                    raise ValueError("Keyboard type changed")

            if media_type and (file_id or media_file):
                media_cls = {
                    "photo": InputMediaPhoto,
                    "video": InputMediaVideo,
                    "document": InputMediaDocument,
                    "animation": InputMediaAnimation,
                }[media_type]
                media = media_cls(media=file_id or media_file, caption=caption)
                await msg.edit_media(media=media, reply_markup=keyboard)
            else:
                await msg.edit_text(caption, reply_markup=keyboard)
            return msg

        except (TelegramBadRequest, ValueError) as e:
            logger.debug(f"Edit failed for {key} ({media_type}): {e}")
            try:
                await msg.delete()
            except TelegramBadRequest:
                pass

    # --- отправка нового сообщения ---
    try:
        if media_type and (file_id or media_file):
            sender = {
                "photo": bot.send_photo,
                "video": bot.send_video,
                "document": bot.send_document,
                "animation": bot.send_animation,
            }[media_type]

            sent: Message = await sender(
                chat_id=chat_id,
                caption=caption,
                reply_markup=keyboard,
                **{media_type: file_id or media_file},
            )

            # кешируем file_id
            if hasattr(sent, "photo") and sent.photo:
                _media_cache[cache_key] = sent.photo[-1].file_id
            elif hasattr(sent, media_type):
                fobj = getattr(sent, media_type, None)
                if hasattr(fobj, "file_id"):
                    _media_cache[cache_key] = fobj.file_id
            logger.debug(f"Cached file_id for {cache_key}")

        else:
            sent = await bot.send_message(chat_id=chat_id, text=caption, reply_markup=keyboard)

    except TelegramBadRequest as e:
        if "file not found" in str(e).lower():
            _media_cache.pop(cache_key, None)
            logger.warning(f"Invalid file_id — cache cleared for {cache_key}")
            return await send_or_edit_message(
                target=target,
                key=key,
                lang=lang,
                text=text,
                keyboard=keyboard,
                bot=bot,
                try_edit=False,
                photo=photo,
                video=video,
                document=document,
                animation=animation,
            )
        else:
            raise

    return sent
