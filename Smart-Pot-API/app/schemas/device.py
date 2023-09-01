from pydantic import BaseModel, Field

from app.schemas.mail import EmailResponse
from app.schemas.utils.device_enums import DeviceNames


class DeviceBase(BaseModel):
    name: str = Field(..., description="Device name")
    type: str = Field(..., description="Device type")


class DeviceResponse(BaseModel):
    id: str
    name: str
    type: str
    user_id: int
    emailResponse: EmailResponse


class DeviceCreate(DeviceBase):
    type: DeviceNames = Field(..., description="Device type")


class DeviceUpdate(DeviceBase):
    pass


class DeviceDB(DeviceBase):
    id: str
    device_token: str
    user_id: int

    class Config:
        orm_mode = True


class Device(DeviceDB):
    pass
