from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.bot.dispatcher import bot, dp, on_startup, on_shutdown
import asyncio

polling_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await on_startup()
    global polling_task
    # Запускаем polling как фоновую задачу (без отдельного потока)
    polling_task = asyncio.create_task(dp.start_polling(bot))
    yield
    # Shutdown
    polling_task.cancel()
    await on_shutdown()

app = FastAPI(title="Bot Service", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}