import os

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

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()  # create an instance of the class
