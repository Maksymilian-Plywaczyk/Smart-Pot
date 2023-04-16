from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String

""" Database user model"""


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    plants = relationship("Plant",back_populates="user")