import uuid
from datetime import datetime
from sqlalchemy import (
    String, Integer, Numeric, Boolean, DateTime, Text,
    Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Listing(Base):
    """
    Объявление об аренде/покупке жилья
    """
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # откуда взято объявление (olx/otodom/xyz) и ID у источника
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # уникальная ссылка на объявление
    url: Mapped[str] = mapped_column(Text, nullable=False)

    # тип сделки: 'rent' | 'sale'
    deal_type: Mapped[str] = mapped_column(String(8), nullable=False)

    # тип объекта: 'apartment' | 'house' | 'room' | ...
    property_type: Mapped[str | None] = mapped_column(String(32), nullable=True)

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    price: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)

    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    district: Mapped[str | None] = mapped_column(String(128), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)

    rooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_total_m2: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    area_living_m2: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    area_kitchen_m2: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    floor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    floors_total: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # актуальность объявления у источника
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # список ссылок на картинки и произвольные флаги/атрибуты
    images: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    attrs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # быстрый dedup: хэш по (source, external_id) или по url/заголовку
    fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external"),
        UniqueConstraint("url", name="uq_url"),
        Index("ix_listings_source_external", "source", "external_id"),
        Index("ix_listings_fingerprint", "fingerprint"),
        Index("ix_listings_city_deal", "city", "deal_type"),
        CheckConstraint("deal_type IN ('rent','sale')", name="ck_deal_type"),
    )
