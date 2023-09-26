from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.plant import Plant
from app.schemas.utils.sensors_type import SensorType

sensor_fields = {
    "hum": Field(..., description="Value of plant humidity", ge=0.0),
    "lux": Field(..., description="Value of plant lux", ge=0.0, le=65535.0),
    "temp": Field(..., description="Value of plant temperature", ge=-40.0, le=85.0),
}


class SensorThresholdBase(BaseModel):
    sensor_name: Optional[str] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    @validator('min_value', 'max_value', pre=True)
    def validate_min_max_values(cls, value, values):
        sensor_name = values.get('sensor_name')
        if sensor_name not in sensor_fields.keys():
            raise ValueError(f"Sensor name {sensor_name} not found")
        return sensor_fields[sensor_name]


class SensorThresholdCreate(SensorThresholdBase):
    sensor_name: Annotated[str, SensorType]
    min_value: int
    max_value: int
    created_at: datetime = Field(default=datetime.utcnow())
    last_updated: datetime = Field(default=datetime.utcnow())


class SensorThresholdUpdate(SensorThresholdBase):
    sensor_name: Annotated[str, SensorType]
    min_value: int
    max_value: int
    last_updated: datetime = Field(default=datetime.utcnow())


class SensorThresholdDB(SensorThresholdBase):
    id: int
    plant_id: int
    plant: Plant = Field(default=..., description="Plant's sensor thresholds")

    class Config:
        orm_mode = True


class SensorThreshold(SensorThresholdDB):
    pass
