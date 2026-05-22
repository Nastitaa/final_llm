import logging
import requests
from app.infra.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task
def llm_request(tg_chat_id: int, prompt: str, system: str = None):
    logger.info(f"Запрос от {tg_chat_id}: {prompt[:50]}...")

    # 1. Вызов OpenRouter
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
        "Content-Type": "application/json",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        answer = resp.json()["choices"][0]["message"]["content"]
        logger.info(f"OpenRouter ответил: {answer[:100]}...")
    except Exception as e:
        logger.error(f"Ошибка OpenRouter: {e}")
        return

    # 2. Отправка ответа в Telegram (прямой вызов Bot API)
    telegram_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        send_resp = requests.post(telegram_url, json={
            "chat_id": tg_chat_id,
            "text": f"🤖 Ответ: {answer}"
        }, timeout=30)
        send_resp.raise_for_status()
        logger.info(f"Сообщение отправлено в чат {tg_chat_id}")
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")