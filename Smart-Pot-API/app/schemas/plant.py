from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.device import Device
from app.schemas.sensors import Sensor


class PlantBase(BaseModel):
    """Base class for Plant Pydantic model"""

    name: Optional[str] = None
    device_id: str
    last_updated: Optional[datetime] = datetime.now()


class PlantCreate(PlantBase):
    """Plant class for creating new one"""

    name: str
    imgsrc: Optional[str] = None
    sensors: Optional[Sensor] = Field(
        default=Sensor(humidity=0.0, lux=0.0, temperature=0.0),
        description="Plant's sensors",
    )


class PlantUpdate(PlantBase):
    """Plant class for receive on plant update"""

    sensors: Sensor
    device_id: Optional[str] = None
    device_token: str


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

    class Config:
        orm_mode = True


class Plant(PlantDB):
    """Plant class for returning via API"""

    pass
