from functools import lru_cache
from typing import Union

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    PROJECT_NAME: str = "SMART-POT-API"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: Union[str, None] = None
    POSTGRES_PASSWORD: Union[str, None] = None
    POSTGRES_DB: Union[str, None] = None
    POSTGRES_SERVER: Union[str, None] = None
    POSTGRES_PORT: Union[int, None] = None  # default port 5432
    FRONTEND_URL: Union[str, None] = None
    SECRET_KEY: Union[str, None] = None
    POSTGRES_TEST_USER: Union[str, None] = None
    POSTGRES_TEST_PASSWORD: Union[str, None] = None
    POSTGRES_TEST_DB: Union[str, None] = None
    EMAIL_TEMPLATE_DIR: str = "app/templates/"
    EMAIL_ADDRESS: Union[str, None] = None
    EMAIL_PASSWORD: Union[str, None] = None
    EMAIL_USERNAME: Union[str, None] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_TIME: int = 60 * 24 * 7  # 7 days
    RESET_PASSWORD_TOKEN_EXPIRE_TIME: int = 60 * 24  # 1 day

    @property
    def PRODUCTION_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@postgres/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@postgres/{self.POSTGRES_TEST_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()  # create an instance of the class

print(settings.PRODUCTION_DATABASE_URL)
