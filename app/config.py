# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "App"
    APP_DIR: str = "app"
    APP_PORT: int = 8000
    ALLOWED_HOSTS: list = ["0.0.0.0", "localhost", "127.0.0.1"]
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/"

    model_config = SettingsConfigDict(env_file=".api.config")


settings = Settings()

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
