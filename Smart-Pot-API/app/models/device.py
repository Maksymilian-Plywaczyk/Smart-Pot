from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base

""" Database device model"""


class Device(Base):
    id = Column(String, index=True, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    type = Column(String, CheckConstraint("type IN ('NODEMCU','ESP')"), nullable=False)
    device_token = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="devices")
    plant = relationship("Plant", back_populates="device")
