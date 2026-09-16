from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    telegram_bot_token: str = ""
    api_base_url: str = "http://api:8000"


settings = BotSettings()
