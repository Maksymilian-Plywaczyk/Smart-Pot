from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base import Base


class SensorThreshold(Base):
    threshold_id = Column(
        String,
        CheckConstraint("threshold_id IN ('temp','lux','hum')"),
        nullable=True,
        primary_key=True,
    )
    min_value = Column(Integer, nullable=False)
    max_value = Column(Integer, nullable=False)
    plant_id = Column(Integer, ForeignKey('plant.id'))
    plant = relationship("Plant", back_populates="sensor_threshold", uselist=False)
