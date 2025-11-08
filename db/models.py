# db/models.py
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import (
    String, Integer, BigInteger, Numeric, Boolean, DateTime, Text, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, Computed, text
)
from urllib.parse import quote_plus
from sqlalchemy.dialects.postgresql import JSONB, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import Enum as SAEnum
from enum import Enum
from time import time
from typing import Any, Optional
import html



class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name_pl: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name_uk: Mapped[str | None] = mapped_column(String(128))
    name_en: Mapped[str | None] = mapped_column(String(128))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_cities_name_pl", "name_pl"),
    )

    def get_name_local(self, lang: str=None) -> str:
        """
        Возвращает название города в нужной локали, если оно есть.
        Fallback-приоритет: lang → uk → pl → en.
        """
        if not lang:
            lang = "uk"

        match lang:
            case "uk":
                return self.name_uk or self.name_pl or self.name_en or self.id
            case "pl":
                return self.name_pl or self.name_uk or self.name_en or self.id
            case "en":
                return self.name_en or self.name_pl or self.name_uk or self.id
            case _:
                # fallback для неизвестного языка
                return self.name_pl or self.name_uk or self.name_en or self.id


class District(Base):
    
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    name_pl: Mapped[str] = mapped_column(String(128), nullable=False)
    name_uk: Mapped[str | None] = mapped_column(String(128))
    name_en: Mapped[str | None] = mapped_column(String(128))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    city: Mapped["City"] = relationship("City")

    def get_name_local(self, lang: str=None) -> str:
        """
        Возвращает название города в нужной локали, если оно есть.
        Fallback-приоритет: lang → uk → pl → en.
        """
        if not lang:
            lang = "uk"

        match lang:
            case "uk":
                return self.name_uk or self.name_pl or self.name_en or self.id
            case "pl":
                return self.name_pl or self.name_uk or self.name_en or self.id
            case "en":
                return self.name_en or self.name_pl or self.name_uk or self.id
            case _:
                # fallback для неизвестного языка
                return self.name_pl or self.name_uk or self.name_en or self.id

    __table_args__ = (
        UniqueConstraint("city_id", "name_pl", name="uq_district_city_namepl"),
        Index("ix_districts_city", "city_id"),
        Index("ix_districts_name_pl", "name_pl"),
    )


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # источник объявления
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_ad_id: Mapped[str] = mapped_column(String(128), nullable=False)

    # типы
    property_type: Mapped[str] = mapped_column(String(16), nullable=False)   # apartment | house | room
    deal_type: Mapped[str] = mapped_column(String(8), nullable=False)        # rent | sale

    # текст
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    # хэш описания для быстрой проверки дублей
    description_hash: Mapped[str | None] = mapped_column(
        String(32),
        Computed("md5(description)", persisted=True),
        index=True
    )
    # переводы
    title_en: Mapped[str | None] = mapped_column(Text)
    title_uk: Mapped[str | None] = mapped_column(Text)
    description_en: Mapped[str | None] = mapped_column(Text)
    description_uk: Mapped[str | None] = mapped_column(Text)
    
    # флаг, что переводы добавлены
    is_translated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ссылки
    url: Mapped[str | None] = mapped_column(Text)
    external_url: Mapped[str | None] = mapped_column(Text)

    # локация (справочники) + адрес
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id", ondelete="SET NULL"))
    address: Mapped[str | None] = mapped_column(Text)

    # метрики
    area_m2: Mapped[float | None] = mapped_column(Numeric(10, 2))
    rooms: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # рынок (primary/secondary и т.п. — если хочешь хранить)
    market: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # флаги
    pets_allowed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    child_allowed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    no_comission: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    
    is_sended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # медиа и сырой payload
    photos: Mapped[list[str] | None] = mapped_column(JSONB)
    tg_photo_id: Mapped[str | None] = mapped_column(String(256), nullable=True, default=None)
    raw: Mapped[dict | None] = mapped_column(JSONB)

    # служебные таймстемпы
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_check: Mapped[int] = mapped_column(
        BigInteger,
        default=lambda: int(time()),     # текущее время в секундах от эпохи
        nullable=False,
        index=True,
    )
    city: Mapped[City] = relationship("City")
    district: Mapped[District | None] = relationship("District")
    
    saved_entries: Mapped[list["SavedListing"]] = relationship(
        "SavedListing",
        back_populates="listing",
        passive_deletes=True,  # доверяем БД (ON DELETE CASCADE)
    )

    @property
    def city_distr_location_str(self) -> str:
        '''
        локация (вместе со вшитой ссылкой на карты)
        '''
        return ", ".join([str(el) for el in [self.city_id, self.district_id] if el is not None])
    

    @property
    def map_url(self) -> str:
        '''
        локация (вместе со вшитой ссылкой на карты)
        '''
        if self.address:
            encoded_address = quote_plus(self.address)
            return f"https://www.google.com/maps?q={encoded_address}"
        return None



    @property
    def first_photo(self) -> str:
        '''
        '''
        if self.photos:
            return self.photos[0]
        return None


    def new_variant_text(self, lang: str='uk') -> str:
        '''
        🏠 Нова квартира знайдена!
        Domio щойно знайшов для тебе свіжу пропозицію напряму від власника 👇

        📍 Місто: [місто]
        💰 Ціна: [ціна]
        📏 Площа: [площа]
        🛏 Кімнат: [кількість]
        📄 Опис: [короткий опис оголошення]
        '''
        res = '🏠 Нова квартира знайдена!\n'
        res += 'Domio щойно знайшов для тебе свіжу пропозицію напряму від власника 👇\n\n'
        return res
    
    def get_title_local(self, lang: str=None) -> str:
        """
        Возвращает название, если оно есть.
        Fallback-приоритет: lang → uk → pl → en.
        """
        if not lang:
            lang = "uk"

        match lang:
            case "uk":
                return self.title_uk or self.title or self.title_en
            case "pl":
                return self.title or self.title_uk or self.title_en
            case "en":
                return self.title_en or self.title or self.title_uk
            case _:
                # fallback для неизвестного языка
                return self.title or self.title_uk or self.title_en
    
    def get_description_local(self, lang: str=None, max_l:int=None) -> str:
        """
        Возвращает название описание, если оно есть.
        Fallback-приоритет: lang → uk → pl → en.
        """
        if not lang:
            lang = "uk"
        res = None
        match lang:
            case "uk":
                res = self.description_uk or self.description or self.description_en
            case "pl":
                res = self.description or self.description_uk or self.description_en
            case "en":
                res = self.description_en or self.description or self.description_uk
            case _:
                # fallback для неизвестного языка
                res = self.description or self.description_uk or self.description_en
        if res and max_l:
            return res[:max_l] + '...'
        return res

    __table_args__ = (
        UniqueConstraint("source", "source_ad_id", name="uq_source_ad"),
        CheckConstraint("property_type IN ('apartment','house','room')", name="ck_property_type"),
        CheckConstraint("deal_type IN ('rent','sale')", name="ck_deal_type"),
        Index(
            "ix_listings_city_prop_deal_desc_hash",
            "city_id", "property_type", "deal_type", "description_hash"
        ),
        Index("ix_listings_city", "city_id"),
        Index("ix_listings_city_deal", "city_id", "deal_type"),
        Index("ix_listings_property_type", "property_type"),
        Index("ix_listings_price", "price"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(64))
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    language_code: Mapped[str | None] = mapped_column(String(8), default=None)

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    recurring_on: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default=text("false"))

    referrer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    referrer: Mapped["User | None"] = relationship(
        "User",
        remote_side=[id],
        backref="referrals"
    )
    # --- Реферальные балансы ---
    # Текущий доступный баланс (можно списывать при оплате/конвертации и т.д.)
    referral_balance_current: Mapped[float] = mapped_column(
        Numeric(14, 2, asdecimal=False),
        default=0,
        nullable=False,
        server_default=text("0"),
        comment="Текущий доступный реферальный баланс (валюта по договорённости)"
    )

    # Всего начислено рефералами за всё время (не уменьшается при трате)
    referral_earnings_total: Mapped[float] = mapped_column(
        Numeric(14, 2, asdecimal=False),
        default=0,
        nullable=False,
        server_default=text("0"),
        comment="Суммарно начислено по реферальной программе за всё время"
    )

    # 🔹 дата до которой активна подписка
    subscription_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Дата и время окончания подписки пользователя (UTC)",
    )
    saved_listing_objs: Mapped[list["SavedListing"]] = relationship(
        "SavedListing", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    saved_listings = association_proxy(
        "saved_listing_objs", "listing",
        creator=lambda listing: SavedListing(listing=listing),
    )

    __table_args__ = (
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_registered_at", "registered_at"),
        Index("ix_users_last_active_at", "last_active_at"),
        Index("ix_users_referral_balance_current", "referral_balance_current"),
    )


    def credit_referral(self, amount: float) -> None:
        """
        Начислить реферальную сумму: увеличиваем и текущий баланс, и total.
        amount должен быть > 0
        """
        # приведение к двум знакам лучше делать на уровне DB/сервисов
        self.referral_balance_current = (self.referral_balance_current or 0) + amount
        self.referral_earnings_total = (self.referral_earnings_total or 0) + amount

    @property
    def subscription_until_str(self) -> str:
        '''
        дату до которой активана подписка в формате ДД.ММ.ГГ ЧЧ:ММ
        '''
        # приводим к таймзоне Варшавы (можешь поменять на нужную)
        if not self.subscription_until:
            return "----"

        dt = self.subscription_until
        # Если вдруг дата на всякий случай наивная — считаем её UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        local_dt = dt.astimezone()   # ← локальная TZ сервера
        return local_dt.strftime("%d.%m.%y %H:%M")
        

    @property
    def display_name(self) -> str:
        name = " ".join(filter(None, [self.first_name, self.last_name])) or (self.username and f"@{self.username}") or "User"
        return html.escape(name)


    @property
    def get_link(self) -> str:
        """
        кликабельная ссылка на юзера
        """
        if self.username:
            href = f"https://t.me/{self.username}"
        else:
            href = f"tg://user?id={self.id}"
        return f'<a href="{href}">{self.display_name}</a>'  

    @property
    def buyer(self) -> dict:
        '''
        возвращает тру если у юзера активна подписка
        '''
        {
            "extCustomerId": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "language": self.language_code,
            }

    @property
    def subscribed(self) -> bool:
        '''
        возвращает тру если у юзера активна подписка
        '''
        if self.subscription_until is not None:
            return self.subscription_until > datetime.now(timezone.utc)
        return False


class FSMState(Base):
    __tablename__ = "fsm_states"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    state: Mapped[str | None] = mapped_column(String(128))
    data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# --- таблица-связка ---
class UserSearchDistrict(Base):
    __tablename__ = "user_search_districts"

    search_id: Mapped[int] = mapped_column(ForeignKey("user_searches.id", ondelete="CASCADE"), primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id", ondelete="CASCADE"), primary_key=True)

    district: Mapped["District"] = relationship("District", overlaps="user_searches,districts")


class UserSearch(Base):
    __tablename__ = "user_searches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", backref="searches")

    deal_type: Mapped[str | None] = mapped_column(String(16))      # rent | sale
    property_type: Mapped[str | None] = mapped_column(String(32))  # apartment | house | room
    market: Mapped[str | None] = mapped_column(String(32), nullable=True)
    
    city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id", ondelete="SET NULL"))
    city: Mapped["City | None"] = relationship("City")

    # 👇 связь many-to-many через промежуточную таблицу
    districts: Mapped[list["District"]] = relationship(
        "District",
        secondary="user_search_districts",
        backref="user_searches",
        cascade="all, delete",
        overlaps="district,user_search_districts",
    )

    # --- диапазоны ---
    area_min: Mapped[float | None] = mapped_column(Numeric(10, 2))
    area_max: Mapped[float | None] = mapped_column(Numeric(10, 2))
    price_min: Mapped[float | None] = mapped_column(Numeric(12, 2))
    price_max: Mapped[float | None] = mapped_column(Numeric(12, 2))

    # --- мультивыбор комнат ---
    rooms: Mapped[list[int] | None] = mapped_column(JSONB)

    pets_allowed: Mapped[bool | None] = mapped_column(Boolean)
    child_allowed: Mapped[bool | None] = mapped_column(Boolean)
    no_comission: Mapped[bool | None] = mapped_column(Boolean, default=True)

    has_confirmed_policy: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_user_search_user_id", "user_id"),
        Index("ix_user_search_city", "city_id"),
    )
    

    def get_str(self, lang: str) -> str:
        """
        Сводка запроса с локализацией: uk / pl / en.
        Показывает:
        - тип сделки, тип недвижимости (+ рынок, если sale)
        - город и районы (если выбраны)
        - площадь (от/до) и комнаты (если НЕ room)
        - стоимость (от/до)
        - наличие животных и детей (только для rent, если указано)
        """
        L = lang
        if L not in ("uk", "pl", "en"):
            L = "uk"

        # ---- словари локализации ----
        DEAL = {
            "rent": {"uk": "Оренда", "pl": "Wynajem", "en": "Rent"},
            "sale": {"uk": "Продаж", "pl": "Sprzedaż", "en": "Sale"},
        }
        PROP = {
            "apartment": {"uk": "Квартира", "pl": "Mieszkanie", "en": "Apartment"},
            "house":     {"uk": "Будинок",  "pl": "Dom",        "en": "House"},
            "room":      {"uk": "Кімната",  "pl": "Pokój",      "en": "Room"},
        }
        MARKET = {
            "primary":   {"uk": "первинний ринок", "pl": "rynek pierwotny",  "en": "primary market"},
            "secondary": {"uk": "вторинний ринок", "pl": "rynek wtórny",     "en": "secondary market"},
        }
        LABEL = {
            "deal":   {"uk": "Угода",      "pl": "Transakcja", "en": "Deal"},
            "type":   {"uk": "Тип",        "pl": "Typ",        "en": "Type"},
            "market": {"uk": "Ринок",      "pl": "Rynek",      "en": "Market"},
            "city":   {"uk": "Місто",      "pl": "Miasto",     "en": "City"},
            "dists":  {"uk": "Райони",     "pl": "Dzielnice",  "en": "Districts"},
            "area":   {"uk": "Площа",      "pl": "Powierzchnia","en": "Area"},
            "rooms":  {"uk": "Кімнат",     "pl": "Pokoje",     "en": "Rooms"},
            "price":  {"uk": "Ціна",       "pl": "Cena",       "en": "Price"},
            "pets":   {"uk": "Тварини",    "pl": "Zwierzęta",  "en": "Pets"},
            "child":  {"uk": "Діти",       "pl": "Dzieci",     "en": "Children"},
            "from":   {"uk": "від",        "pl": "od",         "en": "from"},
            "to":     {"uk": "до",         "pl": "do",         "en": "to"},
            "allowed":    {"uk": "дозволені",   "pl": "dozwolone",  "en": "allowed"},
            "not_allowed":{"uk": "заборонені",  "pl": "niedozwolone","en": "not allowed"},
        }

        def loc(d: dict, key: str) -> str:
            return (d.get(key) or {}).get(L) if isinstance(d.get(key), dict) else None

        def fmt_num(x: float | int | None) -> str:
            if x is None: return ""
            try:
                xi = int(x)
                return str(xi) if xi == x else f"{float(x):.2f}".rstrip("0").rstrip(".")
            except Exception:
                return str(x)

        def fmt_range(lo: float | None, hi: float | None, unit: str = "") -> str:
            if lo is not None and hi is not None:
                s = f"{fmt_num(lo)}–{fmt_num(hi)}"
            elif lo is not None:
                s = f"{LABEL['from'][L]} {fmt_num(lo)}"
            elif hi is not None:
                s = f"{LABEL['to'][L]} {fmt_num(hi)}"
            else:
                return ""
            return f"{s}{(' ' + unit) if unit else ''}"

        parts: list[str] = []

        # --- 1) Сделка / Тип / Рынок (если sale) ---
        if self.deal_type:
            deal_txt = loc(DEAL, self.deal_type) or self.deal_type
            parts.append(f"{LABEL['deal'][L]}: {deal_txt}")
        if self.property_type:
            prop_txt = loc(PROP, self.property_type) or self.property_type
            parts.append(f"{LABEL['type'][L]}: {prop_txt}")
        if self.deal_type == "sale" and self.market:
            mkt_txt = loc(MARKET, self.market) or self.market
            parts.append(f"{LABEL['market'][L]}: {mkt_txt}")

        # --- 2) Город и районы ---
        if self.city:
            # В твоём коде есть city.get_name_local(lang) — используем его, если доступен
            parts.append(f"{LABEL['city'][L]}: {self.city.get_name_local(L)}")

        if self.districts:
            names = [n for n in (d.get_name_local(L) for d in self.districts) if n]
            if names:
                parts.append(f"{LABEL['dists'][L]}: {', '.join(sorted(set(names)))}")

        # --- 3) Площадь и комнаты ---
        area_txt = fmt_range(self.area_min, self.area_max, "m²" if L in ("pl", "en") else "м²")
        if area_txt:
            parts.append(f"{LABEL['area'][L]}: {area_txt}")

        if (self.property_type or "") != "room" and self.rooms:
            # rooms хранится как список ints
            try:
                rooms_list = sorted(set(int(r) for r in self.rooms))
                rooms_txt = ", ".join(str(r) for r in rooms_list)
                parts.append(f"{LABEL['rooms'][L]}: {rooms_txt}")
            except Exception:
                pass

        # --- 4) Стоимость ---
        price_txt = fmt_range(self.price_min, self.price_max)  # без валюты, т.к. не хранится
        if price_txt:
            parts.append(f"{LABEL['price'][L]}: {price_txt}")

        # --- 5) Pets / Children (только для аренды, и только если True) ---
        if self.deal_type == "rent":
            if self.pets_allowed is True:
                parts.append(f"{LABEL['pets'][L]}: {LABEL['allowed'][L]}")
            if self.child_allowed is True:
                parts.append(f"{LABEL['child'][L]}: {LABEL['allowed'][L]}")
        # Финальный многострочный текст
        return "\n".join(parts) if parts else ""


class SavedListing(Base):
    __tablename__ = "saved_listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # ↓ теперь NOT NULL + каскад
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="saved_listing_objs")
    listing: Mapped["Listing"] = relationship("Listing", back_populates="saved_entries")

    __table_args__ = (
        # обычный уникальный (без partial)
        UniqueConstraint("user_id", "listing_id", name="uq_saved_user_listing"),
        Index("ix_saved_listings_user_created", "user_id", "created_at"),
    )


class MessageType(str, Enum):
    REMINDER = "reminder"
    BROADCAST = "broadcast"
    CUSTOM = "custom"
    INVOICE = "invoice"


class ChatType(str, Enum):
    PRIVATE = "private"
    CHANNEL = "channel"


class ScheduledStatus(str, Enum):
    QUEUED = "queued"
    CLAIMED = "claimed"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELED = "canceled"


class ScheduledMessage(Base):
    __tablename__ = "scheduled_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user: Mapped[Optional["User"]] = relationship("User", lazy="joined")

    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # ⬇️ Храним как TEXT + CHECK, без нативного PG ENUM:
    chat_type: Mapped[ChatType] = mapped_column(
        SAEnum(ChatType, name="chat_type", native_enum=False, create_constraint=True),
        nullable=False,
    )

    message_type: Mapped[MessageType] = mapped_column(
        SAEnum(MessageType, name="message_type", native_enum=False, create_constraint=True),
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    send_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    status: Mapped[ScheduledStatus] = mapped_column(
        SAEnum(ScheduledStatus, name="scheduled_status", native_enum=False, create_constraint=True),
        nullable=False,
        server_default=text("'queued'"),  # ❗ теперь без ::scheduled_status
    )

    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))

    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    locked_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    dedup_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    idempotent: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    __table_args__ = (
        Index("ix_sched_status_sendat_prio", "status", "send_at", "priority"),
        Index("ix_sched_user", "user_id"),
        Index("ix_sched_chat", "chat_id"),
        Index(
            "uq_sched_dedup_key_not_null",
            dedup_key,
            unique=True,
            postgresql_where=(dedup_key.is_not(None)),  # <- partial unique
        ),
)


class InvoiceStatus(str, Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"

# задайте свои варианты (подписка/разовый/пакет и т.п.)
class InvoiceType(str, Enum):
    SUBSCRIPTION = "SUBSCRIPTION"
    ONE_TIME = "ONE_TIME"

# === Токены карт ===
# Храним CARD_TOKEN от PayU (значение value), опционально — маску PAN/brand из PayU GET orders
# Один пользователь может иметь несколько токенов; токен уникален глобально.

class UserCardToken(Base):
    __tablename__ = "user_card_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True)     # PayU card token (value)
    last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)   # VISA/MC/...
    exp_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exp_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False)

    user: Mapped["User"] = relationship("User", backref="card_tokens")

    __table_args__ = (
        Index("ix_card_tokens_user_active", "user_id", "is_active"),
    )


# === Инвойсы / Заказы PayU ===

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # связь с пользователем
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user: Mapped["User"] = relationship("User", backref="invoices")
    client_ip: Mapped[str] = mapped_column(String(64), nullable=True)
    redirect_uri: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # тип инвойса (назначение) и "кол-во дней"
    invoice_type: Mapped[InvoiceType] = mapped_column(SAEnum(InvoiceType, name="invoice_type"), default=InvoiceType.SUBSCRIPTION, nullable=False)
    
    subscribe_type: Mapped[str] = mapped_column(String(64), nullable=True)
    days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    next_sub: Mapped[str] = mapped_column(String(64), nullable=True)

    # суммы: в грошах (целые!), валюта
    amount: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # PayU идентификаторы
    payu_order_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True, index=True)       # orderId
    payu_ext_order_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True, index=True)   # extOrderId (ваш)
    payu_payment_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)                  # из properties: PAYMENT_ID

    # статус PayU
    status: Mapped[InvoiceStatus] = mapped_column(SAEnum(InvoiceStatus, name="invoice_status"), default=InvoiceStatus.CREATED, nullable=False)

    # ссылка на сохранённый токен карты (если FIRST → получили токен)
    card_token_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_card_tokens.id", ondelete="SET NULL"), nullable=True)
    card_token: Mapped[Optional["UserCardToken"]] = relationship("UserCardToken")

    # сырой JSON из вебхука/GET orders (последний снимок)
    payu_raw: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # служебные даты
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # когда мы дернули confirm COMPLETED
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # когда получили COMPLETED

    # “мягкие” флаги
    is_refunded: Mapped[bool] = mapped_column(Boolean, default=False)
    is_test: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        # Гарантия: либо extOrderId уникален, либо orderId. Оба — по ситуации.
        # Отдельные unique уже заданы в колонках.
        Index("ix_invoices_user_status", "user_id", "status"),
        Index("ix_invoices_created_at", "created_at"),
    )