# db/repo.py
from __future__ import annotations
from typing import Optional
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func, text
from db.models import City, District, Listing



def upsert_city_by_name_pl(
    s: Session,
    name_pl: str,
    name_uk: Optional[str] = None,
    name_en: Optional[str] = None,
) -> int:

    stmt = (
        insert(City)
        .values(name_pl=name_pl, name_uk=name_uk, name_en=name_en)
        .on_conflict_do_nothing(index_elements=[City.name_pl])
        .returning(City.id)
    )
    new_id = s.execute(stmt).scalar_one_or_none()
    if new_id is not None:
        s.commit()  # фиксируем сразу, как и хотели
        return new_id

    # без lower(): сравнение строгое, регистр уже нормализован в парсере
    return s.execute(
        select(City.id).where(City.name_pl == name_pl)
    ).scalar_one()

def upsert_district_by_name_pl(
    s: Session,
    city_id: int,
    name_pl: str,
    name_uk: Optional[str] = None,
    name_en: Optional[str] = None,
) -> int:

    stmt = (
        insert(District)
        .values(city_id=city_id, name_pl=name_pl, name_uk=name_uk, name_en=name_en)
        .on_conflict_do_nothing(index_elements=[District.city_id, District.name_pl])
        .returning(District.id)
    )
    new_id = s.execute(stmt).scalar_one_or_none()
    if new_id is not None:
        s.commit()
        return new_id

    return s.execute(
        select(District.id).where(
            District.city_id == city_id,
            District.name_pl == name_pl,
        )
    ).scalar_one()


# -------------------------------
#    insert-only: add_listing
# -------------------------------

def add_listing(s: Session, data: dict) -> bool:
    """
    Добавляет листинг, если это не дубль.
    Дубли отбрасываются, если:
      1) пересекаются URL ↔ external_url,
      2) совпадает md5(description) в рамках (city_id, property_type, deal_type),
      3) запись уже существует по (source, source_ad_id).
    При успешной вставке — сразу commit(), иначе False.
    """
    # 0) быстрый предчек по (source, source_ad_id)
    if not data:
        return False
    q_exists = select(Listing.id).where(
        Listing.source == data.get("source"),
        Listing.source_ad_id == data.get("source_ad_id"),
    ).limit(1)
    if s.execute(q_exists).scalar_one_or_none() is not None:
        return False

    # 1) быстрые проверки URL (нормализуем хвостовой '/')
    new_url = data.get("url")
    new_ext = data.get("external_url")
    if new_url or new_ext:
        vals = [v for v in (new_url, new_ext) if v]
        q_url = select(Listing.id).where(
            or_(Listing.url.in_(vals), Listing.external_url.in_(vals))
        ).limit(1)
        if s.execute(q_url).scalar_one_or_none() is not None:
            return False

    # 2) проверка дублей по md5(description) в рамках города/типа/сделки
    new_desc = data.get("description")
    if new_desc:
        q_desc_hash = select(Listing.id).where(
            Listing.city_id == data["city_id"],
            Listing.property_type == data["property_type"],
            Listing.deal_type == data["deal_type"],
            Listing.description_hash == func.md5(new_desc),
        ).limit(1)
        if s.execute(q_desc_hash).scalar_one_or_none() is not None:
            return False

    # 3) вставка (insert-only) + commit
    insert_stmt = (
        insert(Listing)
        .values(**data)
        .on_conflict_do_nothing(index_elements=[Listing.source, Listing.source_ad_id])
        .returning(Listing.id)
    )
    new_id = s.execute(insert_stmt).scalar_one_or_none()
    if new_id is None:
        return False

    s.commit()
    return True


def filter_new_urls(session: Session, urls: list[str], *, chunk_size: int = 1000) -> list[str]:
    """
    Вернёт только новые ссылки (которых нет ни в listings.url, ни в listings.external_url).
    Без нормализации.
    """

    if not urls:
        return []

    # Убираем дубликаты внутри пачки, сохраняя порядок
    seen = set()
    unique_urls: list[str] = []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            unique_urls.append(u)

    if not unique_urls:
        return []

    new_urls: list[str] = []

    # Проверяем по частям, чтобы не превысить лимит параметров
    for start in range(0, len(unique_urls), chunk_size):
        batch = unique_urls[start:start + chunk_size]

        placeholders = ", ".join([f"(:u{i})" for i in range(len(batch))])

        sql = text(f"""
            WITH input(url) AS (
                VALUES {placeholders}
            )
            SELECT DISTINCT i.url
            FROM input i
            LEFT JOIN listings l
              ON l.url = i.url
              OR l.external_url = i.url
            WHERE l.id IS NULL
        """)

        params = {f"u{i}": batch[i] for i in range(len(batch))}
        rows = session.execute(sql, params).fetchall()

        for (u,) in rows:
            new_urls.append(u)

    return new_urls