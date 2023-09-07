import os
from functools import lru_cache

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Settings:
    PROJECT_NAME: str = "SMART-POT-API"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    POSTGRES_SERVER: str = os.getenv('POSTGRES_SERVER')
    POSTGRES_PORT: int = os.getenv('POSTGRES_PORT', 5432)  # default port 5432
    FRONTEND_URL: str = os.getenv('FRONTEND_URL')
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"
    )
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_TIME: int = 60 * 24 * 7  # 7 days


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()  # create an instance of the class
