# db/models.py
from datetime import datetime, timezone
from sqlalchemy import (
    String, Integer, BigInteger, Numeric, Boolean, DateTime, Text, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, Computed
)
from sqlalchemy.dialects.postgresql import JSONB, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.associationproxy import association_proxy
from time import time

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

    referrer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    referrer: Mapped["User | None"] = relationship(
        "User",
        remote_side=[id],
        backref="referrals"
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
    )
    
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
