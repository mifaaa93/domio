import os
from aiogram.types import FSInputFile
from config import ASSET_DIR


def get_image(lang: str | None, key: str) -> FSInputFile | None:
    """
    Возвращает изображение FSInputFile по ключу и языку.
    Ищет файл в приоритетном порядке:

    1. {ASSET_DIR}/{lang}/{key}.(jpg|png|webp)
    2. {ASSET_DIR}/{lang}_{key}.(jpg|png|webp)
    3. {ASSET_DIR}/{key}_{lang}.(jpg|png|webp)
    4. {ASSET_DIR}/{key}.(jpg|png|webp)
    5. {ASSET_DIR}/default/{key}.(jpg|png|webp)
    """
    lang = lang or "uk"

    exts = ["jpg", "png", "webp"]
    patterns = [
        os.path.join(ASSET_DIR, lang, "{key}.{ext}"),
        os.path.join(ASSET_DIR, f"{lang}_{{key}}.{{ext}}"),
        os.path.join(ASSET_DIR, f"{{key}}_{lang}.{{ext}}"),
        os.path.join(ASSET_DIR, "{key}.{ext}"),
        os.path.join(ASSET_DIR, "default", "{key}.{ext}"),
    ]

    for pattern in patterns:
        for ext in exts:
            path = pattern.format(key=key, ext=ext)
            if os.path.exists(path):
                return FSInputFile(path)

    return None
