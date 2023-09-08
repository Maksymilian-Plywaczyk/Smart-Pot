from typing import Annotated, List

import shortuuid
from fastapi import Depends, HTTPException, status
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.crud.crud_users import get_current_active_user, get_user_by_email
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceCreate


def create_id_for_device(device_type: str):
    device_uuid = shortuuid.uuid()
    return f"{device_type}-{device_uuid}"


def get_device_by_id(db: Session, device_id: str):
    device_by_id = db.query(Device).filter(cast(Device.id, String) == device_id).first()
    return device_by_id


def get_current_user_devices(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[Device]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return current_user.devices


def create_new_device(
    new_device: DeviceCreate, db: Session, current_user_id: int, device_token: str
):
    id_as_str = create_id_for_device(new_device.type)
    if get_device_by_id(db, id_as_str):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Device already exist"
        )

    database_device = Device(
        id=id_as_str,
        name=new_device.name,
        type=new_device.type,
        device_token=device_token,
        user_id=current_user_id,
    )
    db.add(database_device)
    db.commit()
    db.refresh(database_device)
    return database_device


def delete_user_device(db: Session, device_id: str, user_email: str):
    db_user = get_user_by_email(db, user_email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    device = get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find device"
        )
    db.delete(device)
    db.commit()
    return {"message": "Device successfully deleted"}
