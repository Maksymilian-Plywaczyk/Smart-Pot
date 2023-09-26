from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class SensorThreshold(Base):
    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(
        String, CheckConstraint("sensor_name IN ('temp','lux','hum')"), nullable=False
    )
    min_value = Column(Integer, nullable=False)
    max_value = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow())
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow())
    plant_id = Column(Integer, ForeignKey('plant.id'))
    plant = relationship("Plant", back_populates="sensor_threshold", uselist=False)
