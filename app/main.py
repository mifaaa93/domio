from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from payu.payu_client import init_payu
from app import miniapp, payments


class CacheAllStatic(StaticFiles):
    async def get_response(self, path: str, scope):
        resp = await super().get_response(path, scope)
        if resp.status_code == 200:
            resp.headers["Cache-Control"] = "no-store"
            #ct = resp.headers.get("Content-Type", "")
            #if "text/html" not in ct.lower():
                #resp.headers["Cache-Control"] = "public, max-age=3600"
            #else:
                #resp.headers["Cache-Control"] = "no-cache"
        return resp


@asynccontextmanager
async def lifespan(app: FastAPI):
    payu = init_payu()
    app.state.payu = payu
    try:
        yield
    finally:
        await payu.aclose()

app = FastAPI(title="Domio API", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"ok": True}

app.mount("/miniapp/static", CacheAllStatic(directory="miniapp/static"), name="miniapp-static")
app.mount("/miniapp", CacheAllStatic(directory="miniapp", html=True), name="miniapp")

app.include_router(miniapp.router, prefix="/api", tags=["miniapp"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
