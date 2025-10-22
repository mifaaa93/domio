import os
from config import ASSET_DIR


def get_image(lang: str | None, key: str) -> str | None:
    """
    Возвращает изображение FSInputFile по ключу и языку.
    Ищет файл в приоритетном порядке:

    1. {ASSET_DIR}/{lang}/{key}.(jpg|png|webp)
    5. {ASSET_DIR}/default/{key}.(jpg|png|webp)
    """
    lang = lang or "uk"

    exts = ["jpg", "png", "webp"]
    patterns = [
        os.path.join(ASSET_DIR, lang, "{key}.{ext}"),
        os.path.join(ASSET_DIR, "default", "{key}.{ext}"),
    ]

    for pattern in patterns:
        for ext in exts:
            path = pattern.format(key=key, ext=ext)
            if os.path.exists(path):
                return path

    return None
