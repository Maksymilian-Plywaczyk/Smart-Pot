from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

PRODUCTION_DATABASE_URL = settings.PRODUCTION_DATABASE_URL
engine = create_engine(PRODUCTION_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
