# db/models.py
from datetime import datetime, timezone
from sqlalchemy import (
    String, Integer, BigInteger, Numeric, Boolean, DateTime, Text, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, Computed
)
from sqlalchemy.dialects.postgresql import JSONB, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
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

    __table_args__ = (
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_registered_at", "registered_at"),
        Index("ix_users_last_active_at", "last_active_at"),
    )


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