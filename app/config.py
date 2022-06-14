import pydantic
from sqlalchemy.engine.url import URL


class Settings(pydantic.BaseSettings):
    SERVICE_NAME: str = "short"
    ROOT_PATH: str = "/"

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    SHORT_URL_TTL: int = 30 * 24 * 60 * 60  # Время, которое короткая ссылка живёт в проекте (в БД)
    # В ТЗ этого не указано, однако в существующих сервисах ссылки живут не бесконечно долго.

    # Redis
    REDIS_URI: str = "redis://redis/1"
    REDIS_URL_KEY: str = "url_{}"  # Ключ, по которому короткая ссылка живёт в Redis
    REDIS_URL_TTL: int = 24 * 60 * 60  # Время, которое короткая ссылка живёт в Redis

    # PostgreSQL
    DB_DRIVER: str = "postgresql+asyncpg"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "short"
    DB_DATABASE: str = "short"
    DB_PASSWORD: str = "short"

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 0
    DB_ECHO: bool = False

    @property
    def DB_DSN(self) -> URL:
        return URL.create(self.DB_DRIVER, self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_DATABASE)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
