# db/repo.py
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, or_, and_, exists
from db.models import City, District, Listing, UserSearch, User, UserSearchDistrict, SavedListing


async def get_user_by_token(session: AsyncSession, user_id: int) -> User | None:
    '''
    возвращает пользователя базы
    '''
    if user_id is None:
        return None

    # 1) Быстрый путь: по первичному ключу
    user = await session.get(User, user_id)
    return user


async def get_listing_by_id(session: AsyncSession, base_id: int) -> Listing | None:
    '''
    '''
    if base_id is None:
        return None

    # 1) Быстрый путь: по первичному ключу
    listing = await session.get(Listing, base_id)
    return listing


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

    result = await session.scalars(
        select(District)
        .where(District.city_id == city_id)
        .order_by(District.name_pl)
    )
    return list(result)
    
# --- НОВОЕ ---
async def find_listings_by_search(
    session: AsyncSession,
    search: UserSearch,
    limit: int = 50,
    offset: int = 0,
    return_total: bool = False,
):
    """
    Ищет объявления Listing, подходящие под фильтр UserSearch.

    Учитываем:
      - deal_type, property_type
      - market (ТОЛЬКО если deal_type == 'sale' и market задан)
      - city_id
      - districts (если заданы — фильтруем по ним)
      - area_min/area_max  -> Listing.area_m2 в диапазоне
      - price_min/price_max -> Listing.price в диапазоне
      - rooms (если property_type != 'room' и список задан)
      - pets_allowed / child_allowed (ТОЛЬКО для rent, и ТОЛЬКО если True —
        тогда требуем совпадение True; False/None игнорируем)

    Сортировка: свежие выше (scraped_at DESC, id DESC).
    Пагинация: limit/offset.
    Если return_total=True — дополнительно вернёт total (COUNT).

    :return:
        (listings, total) если return_total=True
        иначе только listings (list[Listing])
    """
    conditions = []

    # 1) Типы
    if search.deal_type:
        conditions.append(Listing.deal_type == search.deal_type)
    if search.property_type:
        conditions.append(Listing.property_type == search.property_type)

    # 2) Рынок (только для продажи)
    if search.deal_type == "sale" and search.market:
        conditions.append(Listing.market == search.market)

    # 3) Город
    if search.city_id:
        conditions.append(Listing.city_id == search.city_id)

    # 4) Районы
    if search.districts:
        district_ids = [d.id for d in search.districts if d and d.id]
        if district_ids:
            conditions.append(Listing.district_id.in_(district_ids))

    # 5) Площадь (если это не комната)
    if search.property_type != "room":
        if search.area_min is not None:
            conditions.append(Listing.area_m2 >= search.area_min)
        if search.area_max is not None:
            conditions.append(Listing.area_m2 <= search.area_max)

    # 6) Цена
    if search.price_min is not None:
        conditions.append(Listing.price >= search.price_min)
    if search.price_max is not None:
        conditions.append(Listing.price <= search.price_max)

    # 7) Комнаты (если это НЕ комната и список задан)
    if (search.property_type or "") != "room" and search.rooms:
        try:
            parts = []
            for room in [int(r) for r in search.rooms if r is not None]:
                parts.append(Listing.rooms == room)
                if room == 5:
                    parts.append(Listing.rooms > room)

            if parts:
                parts.append(Listing.rooms.is_(None))
                conditions.append(or_(*parts))
        except Exception:
            pass

    # 8) Pets/Children только для аренды:
    #    логика по твоему праву: True -> "можно" => требуем Listing.* == True
    #    False/None -> игнор
    if search.deal_type == "rent":
        if search.pets_allowed is True:
            conditions.append(Listing.pets_allowed.is_not(False))  # True или NULL
        if search.child_allowed is True:
            conditions.append(Listing.child_allowed.is_not(False))  # True или NULL
    if search.no_comission:
        conditions.append(Listing.no_comission.is_(True))
    # Базовый SELECT
    stmt = (
        select(Listing)
        .options(
            selectinload(Listing.city),
            selectinload(Listing.district),
        )
        .where(*conditions)
        .order_by(Listing.scraped_at.desc(), Listing.id.desc())
        .limit(limit)
        .offset(offset)
    )

    listings = list(await session.scalars(stmt))

    if not return_total:
        return listings

    # Отдельный COUNT(*) по тем же условиям
    total_stmt = select(func.count()).select_from(Listing).where(*conditions)
    total = await session.scalar(total_stmt)
    return listings, int(total or 0)


async def find_searches_for_listing(
    session: AsyncSession,
    listing: Listing,
    return_total: bool = False,
):
    """
    Ищет настройки пользователей (UserSearch), которые подходят под данный Listing.
    Учитываются только подтверждённые фильтры (has_confirmed_policy=True).

    Правила соответствуют обратной логике:
      - deal_type/property_type: если в фильтре NULL — не ограничивает; иначе должен совпасть с Listing.*
      - market: учитывается только если deal_type == 'sale' и market в фильтре задан
      - city: либо фильтр.city_id IS NULL, либо = Listing.city_id
      - districts: если у фильтра нет выбранных районов — подходит любой;
                   иначе Listing.district_id должен входить в список (EXISTS)
      - area: применяется, кроме случая, когда фильтр.property_type = 'room'
      - rooms: применяется, если фильтр.property_type != 'room' и rooms задан;
               проверяем, что rooms массива JSONB содержит значение Listing.rooms
      - pets/children: только для аренды; True у фильтра -> требуем True у листинга

    Возвращает:
      - список UserSearch, (и total при return_total=True)
    """
    conds = [UserSearch.has_confirmed_policy.is_(True)]

    # deal_type / property_type: NULL у фильтра => wildcard
    conds.append(UserSearch.deal_type == listing.deal_type)
    conds.append(UserSearch.property_type == listing.property_type)

    # market: только если у фильтра sale и market задан
    conds.append(
        or_(
            UserSearch.deal_type != "sale",
            UserSearch.market.is_(None),
            UserSearch.market == listing.market,
        )
    )

    # city: NULL у фильтра => любой
    conds.append(UserSearch.city_id == listing.city_id)

    # districts: нет выбранных => ок; иначе district_id листинга должен совпасть
    districts_none = ~exists(
        select(UserSearchDistrict.search_id).where(UserSearchDistrict.search_id == UserSearch.id)
    )
    districts_match = exists(
        select(UserSearchDistrict.search_id).where(
            UserSearchDistrict.search_id == UserSearch.id,
            UserSearchDistrict.district_id == listing.district_id,
        )
    )
    conds.append(or_(districts_none, districts_match))

    # area: применяется, кроме случая property_type='room'
    conds.append(
        or_(
            UserSearch.property_type == "room",
            UserSearch.area_min.is_(None),
            Listing.area_m2 >= UserSearch.area_min,
        )
    )
    conds.append(
        or_(
            UserSearch.property_type == "room",
            UserSearch.area_max.is_(None),
            Listing.area_m2 <= UserSearch.area_max,
        )
    )

    # price: если у фильтра нет границ — не ограничивает
    conds.append(or_(UserSearch.price_min.is_(None), Listing.price >= UserSearch.price_min))
    conds.append(or_(UserSearch.price_max.is_(None), Listing.price <= UserSearch.price_max))

    # rooms: только если фильтр.property_type != 'room' и rooms задан
    # Условие: (rooms содержит Listing.rooms) OR (Listing.rooms >= 5 AND rooms содержит 5)
    # Плюс игнорируем правило для фильтров property_type='room' или rooms=NULL.
    conds.append(
        or_(
            UserSearch.property_type == "room",
            UserSearch.rooms.is_(None),
            and_(
                Listing.rooms.is_not(None),
                or_(
                    # точное попадание количества комнат в массив фильтра
                    UserSearch.rooms.contains(func.jsonb_build_array(Listing.rooms)),
                    # 5+ логика: если в фильтре есть 5 и у листинга rooms >= 5
                    and_(
                        Listing.rooms >= 5,
                        UserSearch.rooms.contains(func.jsonb_build_array(5)),
                    ),
                ),
            ),
        )
    )

    # pets/children: только для аренды; True у фильтра -> требуем True у листинга
    # children
    conds.append(
        or_(
            UserSearch.deal_type != "rent",
            UserSearch.child_allowed.is_(None),   # фильтр не включён → не ограничиваем
            UserSearch.child_allowed.is_(False),  # фильтр = False → не ограничиваем
            Listing.child_allowed.is_not(False),  # фильтр = True → листинг НЕ False (True или NULL)
        )
    )

    # pets
    conds.append(
        or_(
            UserSearch.deal_type != "rent",
            UserSearch.pets_allowed.is_(None),
            UserSearch.pets_allowed.is_(False),
            Listing.pets_allowed.is_not(False),   # True или NULL
        )
    )

    stmt = (
        select(UserSearch)
        .options(
            selectinload(UserSearch.city),
            selectinload(UserSearch.districts),
        )
        .where(*conds)
        .order_by(UserSearch.updated_at.desc(), UserSearch.id.desc())
    )

    searches = list(await session.scalars(stmt))

    if not return_total:
        return searches

    total_stmt = select(func.count()).select_from(UserSearch).where(*conds)
    total = await session.scalar(total_stmt)
    return searches, int(total or 0)


async def get_saved_listing_ids(session: AsyncSession, user: User) -> list[int]:
    result = await session.scalars(
        select(SavedListing.listing_id).where(SavedListing.user_id == user.id)
    )
    return result.all()


async def get_apartments_for_user(session: AsyncSession, user: User, page: int, cat: str, lang: str=None) -> list[dict]:
    '''
    for adv in qs[start:end]:
        res.append({
            "base_id": adv.base_id,
            "description": adv.description,
            "price": adv.price_str,
            "city_distr": adv.city_distr_location_str,
            "address": adv.address or '',
            "floor": adv.floor or '',
            "rooms": adv.number_of_rooms_string_from_int,
            "total_floors": adv.total_floors or '',
            "area": adv.total_area or '-',
            "images": adv.all_photo_list,
            "saved": adv.base_id in saved_ids,
            "no_comission": listing.no_comission,
            "property_type": listing.property_type
        })

    return {
        "results": res,
        "total": total,
        "has_next": total>end,
        "cat": cat,
        "total_page": (total + PER_PAGE - 1) // PER_PAGE}
    '''
    limit = 10
    offset = limit*(page-1)
    end = limit*page
    lang = lang or user.language_code or 'uk'
    search = await get_user_search(session, user)
    res = []
    total = 0
    if search.has_confirmed_policy:
        data, total = await find_listings_by_search(session, search, limit, offset, return_total=True)
        if total:
            saved_ids = await get_saved_listing_ids(session, user)
            for listing in data:
                listing: Listing
                city_name = listing.city.get_name_local(lang) if listing.city else ""
                distr_name = listing.district.get_name_local(lang) if listing.district else ""
                city_distr = ", ".join([p for p in (city_name, distr_name) if p])
                res.append({
                "base_id": listing.id,
                "description": listing.description,
                "price": f"{listing.price:.0f} PLN" if listing.price else '-',
                "city_distr": city_distr,
                "address": listing.address or city_distr,
                "rooms": listing.rooms or '-',
                "area": listing.area_m2 or '-',
                "images": listing.photos,
                "saved": listing.id in saved_ids,
                "no_comission": listing.no_comission,
                "property_type": listing.property_type
            })
    return {
        "results": res,
        "total": total,
        "has_next": total>end,
        "cat": cat,
        "total_page": (total + limit - 1) // limit}