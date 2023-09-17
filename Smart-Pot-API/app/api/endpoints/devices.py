import json
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr, parse_obj_as

from app.api.endpoints.tags import Tag
from app.core.dependencies import get_db
from app.core.security import create_device_token
from app.crud.crud_devices import (
    create_new_device,
    delete_user_device,
    get_current_user_devices,
    get_device_by_id,
)
from app.crud.crud_users import get_current_active_user
from app.crud.email_connection import MailConnection
from app.models.user import User
from app.schemas.device import Device, DeviceCreate, DeviceResponse
from app.schemas.mail import Email, EmailResponse
from app.schemas.message import Message

router = APIRouter(prefix="/api/v1/devices", tags=[Tag.DEVICES])


@router.get("/", status_code=200, response_model=List[Device])
def get_current_user_devices(
    devices: Annotated[List[Device], Depends(get_current_user_devices)]
):
    return devices


@router.get("/{device_id}", status_code=200, response_model=Device)
def read_device_by_id(device_id: str, db=Depends(get_db)) -> Device:
    device = get_device_by_id(db=db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find device"
        )
    return device


@router.post(
    "/create-new-device",
    status_code=status.HTTP_201_CREATED,
    response_model=DeviceResponse,
)
async def create_new_device_for_current_user(
    new_device: DeviceCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db=Depends(get_db),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    device_token = create_device_token(length_token=15)
    new_device = create_new_device(
        new_device, db, current_user.id, device_token=device_token
    )
    email_address = EmailStr(current_user.email)
    email = Email(
        email=email_address,
        body={"device_token": device_token, "name": current_user.full_name},
    )
    mail_connection = MailConnection(email)
    response = await mail_connection.send_email_authentication_device_token(
        new_device.id
    )
    email_response = parse_obj_as(EmailResponse, json.loads(response.body))
    return DeviceResponse(
        id=new_device.id,
        name=new_device.name,
        type=new_device.type,
        user_id=new_device.user_id,
        emailResponse=email_response,
    )


@router.delete("/{device_id}", status_code=status.HTTP_200_OK, response_model=Message)
def delete_device_user(
    device_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db=Depends(get_db),
) -> Any:
    user_email = current_user.email
    deleted_message = delete_user_device(db, device_id, user_email)
    return deleted_message
