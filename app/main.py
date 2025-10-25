# app/main.py
from typing import Annotated, Optional
from fastapi import FastAPI, Depends, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import db_session_dep
from db.models import Listing

Db = Annotated[AsyncSession, Depends(db_session_dep)]

app = FastAPI(title="Domio Listings Counter")

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/listings/count")
async def listings_count(db: Db):

    stmt = select(func.count()).select_from(Listing)
    total = await db.scalar(stmt)
    return {"total": int(total or 0)}
