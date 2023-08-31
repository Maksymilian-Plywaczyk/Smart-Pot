from pydantic import BaseModel, Field


class Sensor(BaseModel):
    humidity: float = Field(ge=0.0, description="Value of plant humidity")
    lux: float = Field(ge=0.0, le=65535.0, description="Value of plant lux")
    temperature: float = Field(
        ge=-40.0, le=85.0, description="Value of plant temperature"
    )
