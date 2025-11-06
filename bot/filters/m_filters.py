# bot\filters\m_filters.py
from aiogram.filters import BaseFilter
from db.models import User


class LanguageNotChosen(BaseFilter):
    async def __call__(self, event, user: User | None = None) -> bool:
        return not bool(user and user.language_code)
