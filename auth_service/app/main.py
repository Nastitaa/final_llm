from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.routes_auth import router
from app.core.exceptions import BaseHTTPException
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Auth Service", lifespan=lifespan)
app.include_router(router)

@app.exception_handler(BaseHTTPException)
async def base_http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.get("/health")
async def health():
    return {"status": "ok"}