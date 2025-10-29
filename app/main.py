# app\main.py
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles  # ⬅️ добавили
from app import miniapp, payments

app = FastAPI(title="Domio API")

@app.get("/health")
async def health():
    return {"ok": True}

# 1) Статика: css/fonts/js/images
app.mount(
    "/miniapp/static",
    StaticFiles(directory="miniapp/static"),
    name="miniapp-static",
)

app.mount(
    "/miniapp",
    StaticFiles(directory="miniapp", html=True),
    name="miniapp",
)

# API-роутеры (как у тебя)
app.include_router(miniapp.router, prefix="/api", tags=["miniapp"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])

