from aiogram import Router, types
from aiogram.filters import Command
from app.infra.redis import get_redis
from app.core.jwt import decode_and_validate
from app.tasks.llm_tasks import llm_request
import json

router = Router()

@router.message(Command("token"))
async def save_token(message: types.Message):
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Используйте: /token <ваш_jwt>")
        return
    token = parts[1]
    try:
        payload = decode_and_validate(token)
        user_id = payload["sub"]
        redis = await get_redis()
        key = f"token:{message.from_user.id}"
        await redis.set(key, json.dumps({"token": token, "user_id": user_id}))
        await message.answer("✅ Токен сохранён! Теперь вы можете отправлять сообщения.")
    except ValueError as e:
        await message.answer(f"❌ Неверный токен: {e}")

@router.message()
async def handle_message(message: types.Message):
    redis = await get_redis()
    key = f"token:{message.from_user.id}"
    data_json = await redis.get(key)
    if not data_json:
        await message.answer("⚠️ Сначала отправьте токен командой /token <jwt>")
        return
    data = json.loads(data_json)
    token = data["token"]
    try:
        decode_and_validate(token)  # повторная валидация на всякий случай
    except ValueError as e:
        await message.answer(f"❌ Токен недействителен: {e}. Пожалуйста, получите новый.")
        return

    # Отправляем задачу в Celery
    llm_request.delay(message.from_user.id, message.text, system=None)
    await message.answer("🔄 Ваш запрос обрабатывается...")