from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Plant(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    imgsrc = Column(String, nullable=True)
    humidity = Column(
        Float, nullable=True
    )  # nullable set to True it means that we can have nulls
    lux = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow())
    user_id = Column(Integer, ForeignKey("user.id"))
    device_id = Column(String, ForeignKey("device.id"))
    owner_id = relationship("User", back_populates="plants")
    device = relationship("Device", back_populates="plant", uselist=False)
    plant_hist = relationship("Plant_Hist", back_populates="plant", uselist=False)
    sensor_threshold = relationship(
        "SensorThreshold", back_populates="plant", uselist=True
    )


class Plant_Hist(Base):
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    lux = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow())
    plant_id = Column(Integer, ForeignKey('plant.id'))
    plant = relationship("Plant", back_populates="plant_hist", uselist=False)
