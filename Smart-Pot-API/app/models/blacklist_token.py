from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


class BlackListToken(Base):
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, index=True, unique=True)
    invalidated_at = Column(DateTime, nullable=False)
