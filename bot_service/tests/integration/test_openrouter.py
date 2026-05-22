import pytest
import respx
import httpx 
from httpx import Response
from app.services.openrouter_client import OpenRouterClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_openrouter_ask_success():
    """Успешный запрос к OpenRouter возвращает текст ответа."""
    expected_answer = "FastAPI — это современный веб-фреймворк для Python."
    
    # Мокируем ответ OpenRouter
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": expected_answer
                }
            }
        ]
    }
    
    openrouter_url = f"{settings.openrouter_base_url}/chat/completions"
    
    with respx.mock(base_url=settings.openrouter_base_url) as respx_mock:
        route = respx_mock.post("/chat/completions")
        route.mock(return_value=Response(200, json=mock_response))
        
        client = OpenRouterClient()
        answer = await client.ask(prompt="Что такое FastAPI?")
        
        assert answer == expected_answer
        assert route.called         
        assert len(route.calls) == 1


@pytest.mark.asyncio
async def test_openrouter_ask_with_system():
    """Запрос с системной инструкцией корректно передаётся в OpenRouter."""
    expected_answer = "Краткий ответ: FastAPI — это инструмент для создания API."
    
    mock_response = {
        "choices": [
            {"message": {"content": expected_answer}}
        ]
    }
    
    with respx.mock(base_url=settings.openrouter_base_url) as respx_mock:
        respx_mock.post("/chat/completions").mock(return_value=Response(200, json=mock_response))
        
        client = OpenRouterClient()
        answer = await client.ask(
            prompt="Что такое FastAPI?",
            system="Отвечай максимально кратко, одно предложение."
        )
        
        assert answer == expected_answer
        
        # Проверяем, что в отправленном JSON есть system-сообщение
        request_json = respx_mock.calls[0].request.content
        import json
        body = json.loads(request_json)
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][0]["content"] == "Отвечай максимально кратко, одно предложение."
        assert body["messages"][1]["role"] == "user"


@pytest.mark.asyncio
async def test_openrouter_http_error():
    """Ошибка HTTP от OpenRouter должна пробрасываться как исключение."""
    with respx.mock(base_url=settings.openrouter_base_url) as respx_mock:
        respx_mock.post("/chat/completions").mock(return_value=Response(429, json={"error": "Rate limited"}))
        
        client = OpenRouterClient()
        with pytest.raises(Exception) as exc_info:
            await client.ask("Hello")
        # Проверяем, что исключение содержит информацию об ошибке
        assert "429" in str(exc_info.value) or "Rate limited" in str(exc_info.value)


@pytest.mark.asyncio
async def test_openrouter_network_timeout():
    """Таймаут сети должен обрабатываться как исключение."""
    with respx.mock(base_url=settings.openrouter_base_url) as respx_mock:
        # Симулируем таймаут
        respx_mock.post("/chat/completions").mock(side_effect=httpx.TimeoutException("Timeout"))
        
        client = OpenRouterClient()
        with pytest.raises(Exception) as exc_info:
            await client.ask("Hello")
        assert "Timeout" in str(exc_info.value)


@pytest.mark.asyncio
async def test_openrouter_invalid_json_response():
    """Некорректный JSON от OpenRouter должен вызывать исключение."""
    with respx.mock(base_url=settings.openrouter_base_url) as respx_mock:
        respx_mock.post("/chat/completions").mock(return_value=Response(200, text="Not a json"))
        
        client = OpenRouterClient()
        with pytest.raises(Exception):
            await client.ask("Hello")