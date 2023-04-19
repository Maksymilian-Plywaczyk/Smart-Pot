from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String
from typing import TYPE_CHECKING

""" Database user model"""

if TYPE_CHECKING:
    from .plant import Plant  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    plants = relationship("Plant", back_populates="owner_id")
