from app.db.base import Base
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

"""Database plant model"""


class Plant(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    humidity = Column(Float, nullable=True)  # nullable set to True it means that we can have nulls
    lux = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    owner_id = relationship("User", back_populates="plants")
