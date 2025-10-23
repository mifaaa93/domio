# db/repo.py
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from db.models import City, District, Listing, UserSearch, User


async def get_user_search(session: AsyncSession, user: User) -> UserSearch:
    """
    Возвращает (или создаёт) активный фильтр пользователя UserSearch,
    с заранее подгруженными связями city и districts (selectinload).
    """
    stmt = (
        select(UserSearch)
        .options(
            selectinload(UserSearch.city),
            selectinload(UserSearch.districts),
        )
        .where(UserSearch.user_id == user.id)
    )
    search = await session.scalar(stmt)

    if not search:
        search = UserSearch(user_id=user.id)
        session.add(search)
        await session.commit()
        # повторная загрузка с подгрузкой связей
        search = await session.scalar(stmt)

    return search

async def get_cities(session: AsyncSession, str_names: tuple[str, ...]) -> list[City]:
    """
    Выбираем все города из базы, где name_pl входит в переданный список.
    """
    if not str_names:
        return []

    result = await session.scalars(
        select(City).where(City.name_pl.in_(str_names))
    )
    return list(result)


async def get_districts(session: AsyncSession, city_id: int) -> list[District]:
    """
    Возвращает все районы указанного города по city_id.
    """
    if not city_id:
        return []

    stmt = (
        select(District)
        .join(Listing, Listing.district_id == District.id)
        .where(District.city_id == city_id)
        .group_by(District.id)
        .having(func.count(Listing.id) > 1)
        .order_by(District.name_pl)
    )

    result = await session.scalars(stmt)
    return list(result)