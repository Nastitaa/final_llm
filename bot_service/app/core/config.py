from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "bot-service"
    env: str = "local"
    telegram_bot_token: str
    jwt_secret: str
    jwt_alg: str = "HS256"
    redis_url: str = "redis://redis:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-3.5-turbo"
    openrouter_site_url: str = "https://example.com"
    openrouter_app_name: str = "bot-service"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()