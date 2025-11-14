# db\repo_async.py
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Literal
from sqlalchemy.sql import ColumnElement
from config import REFFERAL_PERCENT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, or_, and_, exists, update, text, asc, desc
from db.models import City, District, Listing, UserSearch, User, UserSearchDistrict, SavedListing, Statistic
from db.models import ScheduledMessage, ScheduledStatus, MessageType, ChatType
from db.models import (
    Invoice, InvoiceStatus, InvoiceType,
    UserCardToken,
)

# ===== статусы: лестница продвижения =====
STATUS_RANK: dict[InvoiceStatus, int] = {
    InvoiceStatus.CREATED: 0,
    InvoiceStatus.PENDING: 1,
    InvoiceStatus.WAITING_FOR_CONFIRMATION: 2,
    InvoiceStatus.COMPLETED: 3,
    InvoiceStatus.CANCELED: 100,   # терминальные
    InvoiceStatus.REJECTED: 100,
}

# Разрешённые значения
SortField = Literal["date", "price", "area", "rooms", "id", "saved"]
SortDir   = Literal["asc", "desc"]

def build_order_by_two(sort_field: str | None,
                       sort_dir: str | None,
                       cat: str) -> list[ColumnElement]:
    """
    sort_field: date | price | area | rooms | id | saved (saved — только для cat='saved')
    sort_dir:   asc | desc
    cat:        'listing' | 'saved'
    """
    sf = (sort_field or "date").lower()
    sd = (sort_dir or "desc").lower()
    is_desc = (sd != "asc")

    # безопасные значения
    allowed_fields = {"date", "price", "area", "rooms", "id"}
    if cat == "saved":
        allowed_fields.add("saved")

    if sf not in allowed_fields:
        sf = "date"

    from db.models import Listing, SavedListing  # локальный импорт, если нужно

    def order(col, is_desc: bool):
        # NULLS LAST, чтобы пустые значения не шли наверх
        return (col.desc() if is_desc else col.asc()).nullslast()

    order_by: list[ColumnElement] = []

    if sf == "date":
        col = SavedListing.created_at if cat == "saved" else Listing.scraped_at
        order_by.append(order(col, is_desc))
    elif sf == "price":
        order_by.append(order(Listing.price, is_desc))
    elif sf == "area":
        order_by.append(order(Listing.area_m2, is_desc))
    elif sf == "rooms":
        order_by.append(order(Listing.rooms, is_desc))
    elif sf == "id":
        order_by.append(order(Listing.id, is_desc))
    elif sf == "saved" and cat == "saved":
        order_by.append(order(SavedListing.created_at, is_desc))
    else:
        # fallback — по дате
        col = SavedListing.created_at if cat == "saved" else Listing.scraped_at
        order_by.append(order(col, True))

    # стабилизатор порядка
    order_by.append(Listing.id.desc().nullslast())
    return order_by


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
    order_by: list=None
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
    elif search.no_comission is False:
        conditions.append(Listing.no_comission.is_not(True))
    # Базовый SELECT
    if not order_by:
        order_by = [Listing.scraped_at.desc(), Listing.id.desc()]
    stmt = (
        select(Listing)
        .options(
            selectinload(Listing.city),
            selectinload(Listing.district),
        )
        .where(*conditions)
        .order_by(*order_by)
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

    if not listing.no_comission:
        conds.append(UserSearch.no_comission.is_not(True))

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



async def get_users_for_listing(session: AsyncSession, listing: Listing) -> list[User]:
    """
    Возвращает уникальных пользователей, чьи фильтры подходят под listing,
    только активных (User.is_active == True).
    """
    if not listing:
        return []

    searches = await find_searches_for_listing(session, listing)
    if not searches:
        return []

    user_ids = {s.user_id for s in searches if s.user_id}
    if not user_ids:
        return []

    users: list[User] = []
    ids_list = list(user_ids)
    chunk_size = 1000

    for i in range(0, len(ids_list), chunk_size):
        chunk = ids_list[i:i + chunk_size]
        result = await session.scalars(
            select(User)
            .where(
                User.id.in_(chunk),
                User.is_active.is_(True),
                User.subscription_until.is_not(None),
                User.subscription_until > func.now(),)
            .order_by(User.id.asc())
        )
        users.extend(result.all())

    return users
    

async def get_saved_listing_ids(session: AsyncSession, user: User) -> list[int]:
    result = await session.scalars(
        select(SavedListing.listing_id).where(SavedListing.user_id == user.id)
    )
    return result.all()


async def get_apartments_for_user(
        session: AsyncSession,
        user: User,
        page: int,
        cat: str,
        lang: str=None,
        sort_field: str=None,
        sort_dir: str=None) -> dict:
    """
    cat: 'listing' | 'saved' (добавлено)
    Возвращает:
      {
        "results": [...],
        "total": int,
        "has_next": bool,
        "cat": str,
        "total_page": int
      }
    """
    limit = 10
    offset = limit * (page - 1)
    end = limit * page
    lang = (lang or user.language_code or 'uk').lower()
    res: list[dict] = []
    total = 0

    # ----- ТОЛЬКО СОХРАНЁННЫЕ -----
    if cat == "saved":
        # total
        total_stmt = (
            select(func.count())
            .select_from(SavedListing)
            .where(SavedListing.user_id == user.id)
        )
        total = int(await session.scalar(total_stmt) or 0)

        if total:
            # сами листинги
            stmt = (
                select(Listing)
                .join(SavedListing, SavedListing.listing_id == Listing.id)
                .where(SavedListing.user_id == user.id)
                .options(
                    selectinload(Listing.city),
                    selectinload(Listing.district),
                )
                .order_by(*build_order_by_two(sort_field, sort_dir, cat))
                .limit(limit)
                .offset(offset)
            )
            listings = list(await session.scalars(stmt))

            for listing in listings:
                city_name = listing.city.get_name_local(lang) if listing.city else ""
                distr_name = listing.district.get_name_local(lang) if listing.district else ""
                city_distr = ", ".join([p for p in (city_name, distr_name) if p])
                res.append({
                    "base_id": listing.id,
                    "description": listing.get_description_local(lang),
                    "price": f"{listing.price:.0f} PLN" if listing.price else '-',
                    "city_distr": city_distr,
                    "address": listing.address or city_distr,
                    "rooms": listing.rooms if listing.rooms is not None else '-',
                    "area": listing.area_m2 if listing.area_m2 is not None else '-',
                    "images": listing.photos,
                    "saved": True,  # тут всегда сохранённое
                    "no_comission": listing.no_comission,
                    "property_type": listing.property_type,
                })

        return {
            "results": res,
            "total": total,
            "has_next": total > end,
            "cat": cat,
            "total_page": (total + limit - 1) // limit,
        }

    # ----- ОСНОВНОЙ СПИСОК ПО ПОИСКУ (как было) -----
    if cat == "listing":
        search = await get_user_search(session, user)
        if search.has_confirmed_policy:
            order_by = build_order_by_two(sort_field, sort_dir, cat)
            data, total = await find_listings_by_search(session, search, limit, offset, return_total=True, order_by=order_by)
            if total:
                saved_ids = await get_saved_listing_ids(session, user)
                saved_ids = set(saved_ids)  # ускорим проверку
                for listing in data:
                    listing: Listing
                    city_name = listing.city.get_name_local(lang) if listing.city else ""
                    distr_name = listing.district.get_name_local(lang) if listing.district else ""
                    city_distr = ", ".join([p for p in (city_name, distr_name) if p])
                    res.append({
                        "base_id": listing.id,
                        "description": listing.get_description_local(lang),
                        "price": f"{listing.price:.0f} PLN" if listing.price else '-',
                        "city_distr": city_distr,
                        "address": listing.address or city_distr,
                        "rooms": listing.rooms if listing.rooms is not None else '-',
                        "area": listing.area_m2 if listing.area_m2 is not None else '-',
                        "images": listing.photos,
                        "saved": listing.id in saved_ids,
                        "no_comission": listing.no_comission,
                        "property_type": listing.property_type,
                    })

        return {
            "results": res,
            "total": total,
            "has_next": total > end,
            "cat": cat,
            "total_page": (total + limit - 1) // limit,
        }

    # ----- на будущее: другие категории (last_week и т.п.) -----
    # По умолчанию вернём пустой результат для неизвестной категории
    return {
        "results": [],
        "total": 0,
        "has_next": False,
        "cat": cat,
        "total_page": 0,
    }

async def schedule_message(
    session: AsyncSession,
    message_type: MessageType,
    chat_type: ChatType,
    payload: dict[str, Any],
    send_at: datetime=None,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None,
    priority: int = 0,
    dedup_key: Optional[str] = None,
    max_attempts: int = 5,
) -> ScheduledMessage:
    """
    Поставить в очередь одно сообщение.
    Если dedup_key задан и уже есть запись с тем же ключом — кину IntegrityError (лови снаружи)
    или сделай upsert на уровне вызова по необходимости.
    """
    send_at = send_at or datetime.now(timezone.utc)
    msg = ScheduledMessage(
        user_id=user_id,
        chat_id=chat_id,
        chat_type=chat_type,
        message_type=message_type,
        priority=priority,
        send_at=send_at,
        payload=payload or {},
        status=ScheduledStatus.QUEUED,
        max_attempts=max_attempts,
        dedup_key=dedup_key,
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg

async def claim_due_messages(
    session: AsyncSession,
    *,
    worker_id: str,
    now: Optional[datetime] = None,
    limit: int = 50,
) -> list[ScheduledMessage]:
    """
    Захватывает готовые к отправке сообщения (status=queued, send_at<=now),
    проставляет locked_by/locked_at и переводит в CLAIMED.
    Использует SELECT ... FOR UPDATE SKIP LOCKED для конкурентных воркеров.
    """
    now = now or datetime.now(timezone.utc)

    # 1) Выбираем id задач, которые пора делать
    subq = (
        select(ScheduledMessage.id)
        .where(
            ScheduledMessage.status == ScheduledStatus.QUEUED,
            ScheduledMessage.send_at <= now,
        )
        .order_by(ScheduledMessage.priority.desc(), ScheduledMessage.send_at.asc(), ScheduledMessage.id.asc())
        .limit(limit)
        .with_for_update(skip_locked=True)
    )

    ids = list(await session.scalars(subq))
    if not ids:
        return []

    # 2) Обновляем их атомарно
    await session.execute(
        update(ScheduledMessage)
        .where(ScheduledMessage.id.in_(ids))
        .values(
            status=ScheduledStatus.CLAIMED,
            locked_by=worker_id,
            locked_at=func.now(),
        )
    )
    await session.commit()

    # 3) Возвращаем полные записи
    result = await session.scalars(
        select(ScheduledMessage)
        .options(selectinload(ScheduledMessage.user))
        .where(ScheduledMessage.id.in_(ids))
        .order_by(ScheduledMessage.priority.desc(), ScheduledMessage.id.asc())
    )
    return list(result)

async def mark_sending(session: AsyncSession, msg_id: int):
    await session.execute(
        update(ScheduledMessage)
        .where(ScheduledMessage.id == msg_id)
        .values(status=ScheduledStatus.SENDING)
    )
    await session.commit()

async def mark_sent(session: AsyncSession, msg_id: int):
    await session.execute(
        update(ScheduledMessage)
        .where(ScheduledMessage.id == msg_id)
        .values(status=ScheduledStatus.SENT)
    )
    await session.commit()

async def mark_retry(
    session: AsyncSession, msg_id: int, *, last_error: Optional[str] = None
):
    """
    Увеличивает attempts. Если attempts достиг max_attempts — переводит в FAILED.
    Иначе возвращает в QUEUED (можно добавить backoff на send_at при желании).
    """
    # Получим текущее состояние
    row = await session.get(ScheduledMessage, msg_id)
    if not row:
        return
    attempts = (row.attempts or 0) + 1
    new_status = ScheduledStatus.FAILED if attempts >= (row.max_attempts or 5) else ScheduledStatus.QUEUED

    values = {
        "attempts": attempts,
        "status": new_status,
        "last_error": last_error,
        "locked_by": None,
        "locked_at": None,
    }
    # простой backoff: +60 сек * attempts
    if new_status == ScheduledStatus.QUEUED:
        values["send_at"] = func.now() + text(f"interval '{60 * attempts} seconds'")

    await session.execute(
        update(ScheduledMessage)
        .where(ScheduledMessage.id == msg_id)
        .values(**values)
    )
    await session.commit()

async def cancel_message(session: AsyncSession, msg_id: int):
    await session.execute(
        update(ScheduledMessage)
        .where(ScheduledMessage.id == msg_id, ScheduledMessage.status.in_([ScheduledStatus.QUEUED, ScheduledStatus.CLAIMED]))
        .values(status=ScheduledStatus.CANCELED)
    )
    await session.commit()

async def add_sub_to_user(
        session: AsyncSession,
        user: User,
        days: int,
        amount: float=None,
        is_test: bool=False) -> None:
    """
    Продлевает подписку пользователя на `days` суток.
    Если подписки нет или она уже истекла — начинает отсчёт от текущего времени (UTC).
    Возвращает новое значение subscription_until (UTC).
    если amount то засчитываем реферальный баланс реффералу
    """
    if days <= 0:
        # ничего не меняем — возвращаем текущее значение (или now, если его нет)
        return

    now = datetime.now(timezone.utc)
    base = user.subscription_until if (user.subscription_until and user.subscription_until > now) else now
    new_until = base + timedelta(days=days)
    user.subscription_until = new_until
    user.is_full_sub = not is_test or user.is_full_sub
    
    if amount and user.referrer_id:
        # 
        value = amount*REFFERAL_PERCENT
        refferal = await get_user_by_token(session, user.referrer_id)
        if refferal:
            refferal.credit_referral(value)
    if amount:
        user.recurring_on = True

    await session.flush()  # фиксация изменений в текущей транзакции (commit делает вызывающий код)


async def disable_sub_to_user(session: AsyncSession, user: User) -> None:
    """
    Продлевает подписку пользователя на `days` суток.
    Если подписки нет или она уже истекла — начинает отсчёт от текущего времени (UTC).
    Возвращает новое значение subscription_until (UTC).
    """
    user.subscription_until = None
    await session.commit()  # фиксация изменений в текущей транзакции (commit делает вызывающий код)


async def create_invoice(
    session: AsyncSession,
    *,
    user_id: Optional[int],
    invoice_type: InvoiceType,
    amount: float,
    currency: str = "PLN",
    description: Optional[str] = None,
    days: Optional[int] = None,
    subscribe_type: Optional[str] = None,
    payu_ext_order_id: Optional[str] = None,
    client_ip: str = None,
    is_test: bool = False,
    next_sub: str=None,
    reuse_window_minutes: int = 60,   # ← окно переиспользования
) -> Invoice:
    """
    Ищет и переиспользует уже созданный инвойс (CREATED + redirect_uri IS NOT NULL)
    за последние N минут по ключам (user_id, invoice_type, amount, currency, subscribe_type).
    Если не найден — создаёт новый (status=CREATED).
    """
    # нормализуем сумму к Decimal

    # --- 1) Пытаемся найти подходящий инвойс за последние N минут ---
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=reuse_window_minutes)

    stmt = (
        select(Invoice)
        .where(
            Invoice.user_id == user_id,
            Invoice.invoice_type == invoice_type,
            Invoice.amount == amount,
            Invoice.currency == currency,
            Invoice.subscribe_type == subscribe_type,
            Invoice.status == InvoiceStatus.CREATED,
            Invoice.redirect_uri.is_not(None),      # непустая ссылка
            Invoice.created_at >= cutoff,
        )
        .order_by(Invoice.created_at.desc())
        .limit(1)
    )
    res = await session.execute(stmt)
    existing = res.scalar_one_or_none()
    if existing:
        return existing

    # --- 2) Иначе создаём новый черновик ---
    inv = Invoice(
        user_id=user_id,
        invoice_type=invoice_type,
        amount=amount,                      # Numeric(10,2)
        currency=currency,
        description=description,
        days=days,
        subscribe_type=subscribe_type,
        payu_ext_order_id=payu_ext_order_id,
        is_test=is_test,
        client_ip=client_ip,
        next_sub=next_sub,
        status=InvoiceStatus.CREATED,
    )
    session.add(inv)
    await session.flush()  # получим inv.id
    return inv

# ---------- LOOKUPS ----------

async def get_invoice_by_id(session: AsyncSession, invoice_id: int) -> Optional[Invoice]:
    res = await session.execute(select(Invoice).where(Invoice.id == invoice_id))
    return res.scalar_one_or_none()

async def get_invoice_by_order_id(session: AsyncSession, order_id: str) -> Optional[Invoice]:
    res = await session.execute(select(Invoice).where(Invoice.payu_order_id == order_id))
    return res.scalar_one_or_none()

async def get_invoice_by_ext_order_id(session: AsyncSession, ext_order_id: str) -> Optional[Invoice]:
    res = await session.execute(select(Invoice).where(Invoice.payu_ext_order_id == ext_order_id))
    return res.scalar_one_or_none()

# ---------- PAYU REFERENCES / SNAPSHOT ----------

async def attach_payu_order_refs(
    session: AsyncSession,
    invoice_id: int,
    *,
    order_id: Optional[str] = None,
    ext_order_id: Optional[str] = None,
    payment_id: Optional[str] = None,
    payu_raw: Optional[dict] = None,
    redirect_uri: Optional[str] = None,
) -> None:
    """Привязывает orderId/extOrderId/paymentId и опционально обновляет raw снапшот."""
    values: dict = {}
    if order_id is not None:
        values["payu_order_id"] = order_id
    if ext_order_id is not None:
        values["payu_ext_order_id"] = ext_order_id
    if payment_id is not None:
        values["payu_payment_id"] = payment_id
    if payu_raw is not None:
        values["payu_raw"] = payu_raw
    if redirect_uri is not None:
        values["redirect_uri"] = redirect_uri

    if values:
        await session.execute(update(Invoice).where(Invoice.id == invoice_id).values(**values))


async def record_webhook_snapshot(
    session: AsyncSession,
    invoice: Invoice,
    *,
    payu_raw: Optional[dict],
    status: Optional[InvoiceStatus] = None,
) -> bool:
    """
    Обновляет payu_raw и, если status задан, продвигает статус идемпотентно.
    Возвращает True, если статус изменился.
    """
    changed = False
    if payu_raw is not None:
        invoice.payu_raw = payu_raw

    if status is not None:
        changed = await advance_status(session, invoice, status)

    await session.flush()
    return changed

# ---------- STATUS ADVANCE (IDEMPOTENT) ----------

async def advance_status(
    session: AsyncSession,
    invoice: Invoice,
    new_status: InvoiceStatus,
) -> bool:
    """Продвигает статус по лестнице. Таймштампы: confirmed_at при нашем confirm; completed_at при COMPLETED."""
    cur = invoice.status
    if STATUS_RANK.get(new_status, -1) > STATUS_RANK.get(cur, -1):
        invoice.status = new_status
        now = datetime.now(timezone.utc)
        if new_status == InvoiceStatus.COMPLETED and invoice.completed_at is None:
            invoice.completed_at = now
        await session.flush()
        return True
    return False

async def mark_confirmed_now(session: AsyncSession, invoice: Invoice) -> None:
    """Фиксирует момент, когда мы дернули confirm → COMPLETED (двухфазный сценарий)."""
    invoice.confirmed_at = datetime.now(timezone.utc)
    await session.flush()

# ---------- CARD TOKEN ----------

async def upsert_card_token(
    session: AsyncSession,
    user_id: int,
    token: str,
    *,
    last4: Optional[str] = None,
    brand: Optional[str] = None,
    exp_month: Optional[int] = None,
    exp_year: Optional[int] = None,
) -> UserCardToken:
    """Создаёт/реактивирует токен карты. Уникальность token обеспечена на уровне модели."""
    res = await session.execute(select(UserCardToken).where(UserCardToken.token == token))
    ct = res.scalar_one_or_none()
    if ct:
        # обновим данные, если что-то новое пришло
        ct.is_active = True
        if last4 is not None:
            ct.last4 = last4
        if brand is not None:
            ct.brand = brand
        if exp_month is not None:
            ct.exp_month = exp_month
        if exp_year is not None:
            ct.exp_year = exp_year
    else:
        ct = UserCardToken(
            user_id=user_id,
            token=token,
            last4=last4,
            brand=brand,
            exp_month=exp_month,
            exp_year=exp_year,
            is_active=True,
        )
        session.add(ct)
        await session.flush()
    return ct

async def link_card_token_to_invoice(session: AsyncSession, invoice: Invoice, ct: UserCardToken) -> None:
    invoice.card_token_id = ct.id
    await session.flush()

# ---------- HELPERS для потройки PIPELINE ----------

async def set_pending_after_create(session: AsyncSession, invoice: Invoice) -> None:
    """Удобно вызывать сразу после успешного create_order в PayU (когда получили redirectUri)."""
    await advance_status(session, invoice, InvoiceStatus.PENDING)

async def set_waiting_for_confirmation(session: AsyncSession, invoice: Invoice) -> None:
    await advance_status(session, invoice, InvoiceStatus.WAITING_FOR_CONFIRMATION)

async def set_completed(session: AsyncSession, invoice: Invoice) -> None:
    ok = await advance_status(session, invoice, InvoiceStatus.COMPLETED)
    if ok and invoice.completed_at is None:
        invoice.completed_at = datetime.now(timezone.utc)
    await session.flush()


async def add_statistic_data(
    session: AsyncSession,
    user: User | None,
    menu_item: str,
    menu_task: str,
    payload: dict,
) -> None:
    """
    Добавляем запись в таблицу statistics.
    payload возможные ключи:
      - key: str
      - city_id: int
      - chat_id: int
      - message_id: int
      - lang: str
      - user_agent: str
      - ... любые дополнительные поля (они будут в payload JSONB)
    Функция делает session.add() + await session.flush() — не коммитит (commit контролирует вызывающий код).
    """
    key = payload.get("key")
    city_id = payload.get("city_id")
    chat_id = payload.get("chat_id")
    message_id = payload.get("message_id")
    lang = payload.get("lang") or (getattr(user, "language_code", None) if user else None)
    user_agent = payload.get("user_agent")

    stat = Statistic(
        user_id=(user.id if user else None),
        city_id=city_id,
        menu_item=menu_item,
        menu_task=menu_task,
        key=key,
        payload=payload or {},
        chat_id=chat_id,
        message_id=message_id,
        lang=lang,
        user_agent=user_agent,
    )

    session.add(stat)
    # flush — чтобы получить id и убедиться, что запись создана в текущей транзакции
    await session.commit()