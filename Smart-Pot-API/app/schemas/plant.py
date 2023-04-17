from pydantic import BaseModel, Field
from typing import Optional


class PlantBase(BaseModel):
    """Base class for Plant Pydantic model"""
    name: Optional[str] = None


class PlantCreate(PlantBase):
    """Plant class for creating new one"""
    name: str


class PlantUpdate(PlantBase):
    """Plant class for receive on plant update"""
    pass


class PlantDB(PlantBase):
    """ Plant model as model from database"""
    id: int
    humidity: Optional[float] = Field(ge=0.0, le=0.0, decimal_places=2, description="Value of plant humidity")
    lux: Optional[float] = Field(ge=1.0, le=65535.0, decimal_places=2, description="Value of plant lux")
    temperature: Optional[float] = Field(ge=-40.0, le=85.0, decimal_places=2, description="Value of plant temperature")
    owner_id: int

    class Config:
        orm_mode = True


class Plant(PlantDB):
    """ Plant class for returning via API"""
    pass
