import pytest
from unittest.mock import patch, AsyncMock
from aiogram.types import Message, Chat, User
from app.bot.handlers import save_token, handle_message

@pytest.mark.asyncio
async def test_token_handler(fake_redis):
    msg = Message(
        message_id=1,
        date=0,
        chat=Chat(id=1, type="private"),
        from_user=User(id=123, is_bot=False, first_name="test"),
        text="/token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMifQ.xxx"
    )
    # Патчим метод answer у класса Message
    with patch('aiogram.types.Message.answer', new_callable=AsyncMock) as mock_answer:
        with patch("app.bot.handlers.decode_and_validate") as mock_decode:
            mock_decode.return_value = {"sub": "123"}
            await save_token(msg)

    mock_answer.assert_called_once_with("✅ Токен сохранён! Теперь вы можете отправлять сообщения.")
    
    redis = await fake_redis
    val = await redis.get("token:123")
    assert val is not None

@pytest.mark.asyncio
async def test_no_token(fake_redis):
    msg = Message(
        message_id=1,
        date=0,
        chat=Chat(id=1, type="private"),
        from_user=User(id=123, is_bot=False, first_name="test"),
        text="hello"
    )
    with patch('aiogram.types.Message.answer', new_callable=AsyncMock) as mock_answer:
        with patch("app.bot.handlers.llm_request.delay") as mock_delay:
            await handle_message(msg)
            mock_delay.assert_not_called()
    
    mock_answer.assert_called_once_with("⚠️ Сначала отправьте токен командой /token <jwt>")