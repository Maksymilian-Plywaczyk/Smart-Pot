from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from ..schemas.device import Device
from ..schemas.sensor_threshold import SensorThreshold
from ..schemas.sensors import Sensor


class PlantBase(BaseModel):
    """Base class for Plant Pydantic model"""

    name: Optional[str] = None
    device_id: Optional[str] = None
    last_updated: Optional[datetime] = datetime.now()


class PlantCreate(PlantBase):
    """Plant class for creating new one"""

    name: str
    imgsrc: Optional[str] = None
    device_id: str
    sensors: Optional[Sensor] = Field(
        default=Sensor(humidity=0.0, lux=0.0, temperature=0.0),
        description="Plant's sensors",
    )


class PlantUpdate(PlantBase):
    """Plant class for receive on plant update"""

    sensors: Sensor
    device_token: str


class ChangePlantName(BaseModel):
    name: str


class PlantDB(PlantBase):
    """Plant model as model from database"""

    id: int
    humidity: float = Field(ge=0.0, description="Value of plant humidity")
    lux: float = Field(ge=0.0, le=65535.0, description="Value of plant lux")
    temperature: float = Field(
        ge=-40.0, le=85.0, description="Value of plant temperature"
    )
    imgsrc: str
    user_id: int
    device_id: str
    device: Device = Field(default=..., description="Plant's device")
    sensor_threshold: List[SensorThreshold] = Field(
        default=[], description="Plant's sensor thresholds"
    )

    class Config:
        orm_mode = True


class Plant(PlantDB):
    """Plant class for returning via API"""

    pass


class PlantHist(BaseModel):
    id: int
    temperature: float = Field(
        ge=-40.0, le=85.0, description="Value of plant temperature"
    )
    lux: float = Field(ge=0.0, le=65535.0, description="Value of plant lux")
    humidity: float = Field(ge=0.0, description="Value of plant humidity")
    added_at: datetime
    plant_id: int

    class Config:
        orm_mode = True
