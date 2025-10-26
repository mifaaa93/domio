# app\main.py
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles  # ⬅️ добавили
from app import miniapp, payments

app = FastAPI(title="Domio API")

@app.get("/health")
async def health():
    return {"ok": True}

app.mount(
    "/miniapp/result",
    StaticFiles(directory="miniapp/result", html=True),
    name="miniapp-result",
)

# API-роутеры (как у тебя)
app.include_router(miniapp.router, prefix="/api", tags=["miniapp"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])

