from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.utils.sensors_type import SensorType

sensor_fields = {
    "hum": {"min_val": 0, "max_val": 100},
    "lux": {"min_val": 0, "max_val": 65535},
    "temp": {"min_val": -40, "max_val": 85},
}


class SensorThresholdBase(BaseModel):
    sensor_name: Optional[str] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    @validator('min_value', 'max_value', pre=True, always=True)
    def validate_min_max_values(cls, value, values):
        sensor_name = values.get('sensor_name')
        if sensor_name not in sensor_fields:
            raise ValueError(f"Sensor name '{sensor_name}' not found in sensor_fields.")

        if not (
            sensor_fields[sensor_name]["min_val"]
            <= value
            <= sensor_fields[sensor_name]["max_val"]
        ):
            raise ValueError(
                f"min_value should be between {sensor_fields[sensor_name].ge}"
                f" and {sensor_fields[sensor_name].le} for sensor '{sensor_name}'"
            )
        return value


class SensorThresholdCreate(SensorThresholdBase):
    sensor_name: Annotated[str, SensorType]
    min_value: int
    max_value: int
    created_at: datetime = Field(default=datetime.utcnow())
    last_updated: datetime = Field(default=datetime.utcnow())


class SensorThresholdUpdate(BaseModel):
    min_value: int
    max_value: int
    last_updated: datetime = Field(default=datetime.utcnow())


class SensorThresholdDB(SensorThresholdBase):
    id: int
    plant_id: int

    class Config:
        orm_mode = True


class SensorThreshold(SensorThresholdDB):
    pass
