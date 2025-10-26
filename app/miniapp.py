from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.deps import db_session_dep
from app.validator import valid_user_from_header, MiniAppAuth
from db.models import Listing

router = APIRouter()

Db = Annotated[AsyncSession, Depends(db_session_dep)]
Auth = Annotated[MiniAppAuth, Depends(valid_user_from_header)]

@router.get("/listings/count")
async def listings_count(session: Db, auth_user: Auth):
    total = await session.scalar(select(func.count()).select_from(Listing))
    return {
        "total": int(total or 0),
        "user": auth_user.get("user"),  # пример использования
    }
