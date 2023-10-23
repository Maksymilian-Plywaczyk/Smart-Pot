from datetime import datetime, timezone
from typing import Annotated, Any, List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import verify_device_token
from ..crud.crud_devices import get_device_by_id, get_device_by_token
from ..crud.crud_users import get_current_active_user, get_user_by_email
from ..models.device import Device
from ..models.plant import Plant as PlantDB
from ..models.plant import Plant_Hist
from ..models.user import User
from ..schemas.plant import ChangePlantName, Plant, PlantCreate, PlantUpdate


def convert_string_date_to_datetime(date: str, _format: str = "%Y-%m-%d") -> datetime:
    try:
        date_as_datetime = datetime.strptime(date, _format)
        return date_as_datetime
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong date format, accepted format is YYYY-MM-DD",
        )


# TODO move sqlalchemy filter statement to 2.0 version
def get_plant_by_id(db: Session, plant_id: int):
    # plant_by_id = db.execute(select(PlantDB).filter_by(id=plant_id).limit(1)).first()
    plant_by_id = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    return plant_by_id


def get_user_plant_by_id(db: Session, plant_id: int, user_id: int):
    plant_by_id = (
        db.query(PlantDB)
        .filter(PlantDB.id == plant_id, PlantDB.user_id == user_id)
        .first()
    )
    return plant_by_id


def delete_plant_hist_by_plant_id(db: Session, plant_id: int):
    plant_hist = db.query(Plant_Hist).filter(Plant_Hist.plant_id == plant_id).delete()
    db.commit()
    return plant_hist


def get_plant_by_device_token(db: Session, device_token: str):
    plant_by_device = (
        db.query(PlantDB)
        .join(Device, PlantDB.device_id == Device.id)
        .filter(Device.device_token == device_token)
        .first()
    )
    return plant_by_device


def get_plant_by_device_id(db: Session, plant_device_id: str):
    plant_by_device = (
        db.query(PlantDB).filter(PlantDB.device_id == plant_device_id).first()
    )
    return plant_by_device


def get_current_user_plants(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[Plant]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return current_user.plants


def create_new_plant(new_plant: PlantCreate, db: Session, user_id: int):
    user_device = get_device_by_id(db, new_plant.device_id)
    if not user_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find device name"
        )
    database_plant = PlantDB(
        name=new_plant.name,
        humidity=new_plant.sensors.humidity,
        imgsrc=new_plant.imgsrc,
        lux=new_plant.sensors.lux,
        temperature=new_plant.sensors.temperature,
        last_updated=new_plant.last_updated,
        device_id=user_device.id,
        user_id=user_id,
    )
    db.add(database_plant)
    db.commit()
    db.refresh(database_plant)
    return database_plant


def save_plant_history_data(db: Session, plant_db: PlantDB) -> Any:
    plant_hist = Plant_Hist(
        temperature=plant_db.temperature,
        lux=plant_db.lux,
        humidity=plant_db.humidity,
        added_at=plant_db.last_updated,
        plant_id=plant_db.id,
    )
    db.add(plant_hist)
    db.commit()
    db.refresh(plant_hist)
    return plant_hist


def update_plant(db: Session, updated_plant: PlantUpdate) -> Any:
    db_device = get_device_by_token(db, updated_plant.device_token)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User cannot update plant with not exisiting device",
        )
    db_plant = get_plant_by_device_token(db, device_token=updated_plant.device_token)
    if not db_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot find plant with that device",
        )
    if not verify_device_token(
        db_plant.device.device_token, updated_plant.device_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot verify device token",
        )
    save_plant_history_data(db, db_plant)
    plant_data = updated_plant.dict(exclude_unset=True)
    for key, value in plant_data.items():
        if key == 'sensors':
            for sensor_key, sensor_value in value.items():
                setattr(db_plant, sensor_key, sensor_value)
        setattr(db_plant, key, value)
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant


def update_plant_name(
    db: Session, changed_name_plant: ChangePlantName, plant_id: int
) -> Any:
    db_plant = get_plant_by_id(db=db, plant_id=plant_id)
    if not db_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot find plant with that id",
        )
    plant_data = changed_name_plant.dict(exclude_unset=True)
    for key, value in plant_data.items():
        setattr(db_plant, key, value)
    db.add(db_plant)
    db.commit()
    db.refresh()
    return db_plant


def delete_user_plant(plant_id: int, db: Session, user_email: str) -> Any:
    db_user = get_user_by_email(db, user_email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db_plant = get_plant_by_id(db, plant_id)
    if not db_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found"
        )
    delete_plant_hist_by_plant_id(db, plant_id)
    db.delete(db_plant)
    db.commit()
    return {"message": "Plant deleted successfully"}


def get_user_historical_plant_data_limit(db: Session, plant_id: int, limit: int):
    plant_hist = (
        db.query(Plant_Hist)
        .filter(Plant_Hist.plant_id == plant_id)
        .order_by(Plant_Hist.added_at.desc())
        .limit(limit)
        .all()
    )

    return plant_hist


def get_user_historical_plant_data_by_date(
    db: Session, plant_id: int, start_at: str, end_at: Optional[str]
):
    if end_at is None:
        end_at_as_datetime = datetime.now(timezone.utc)
    else:
        end_at_as_datetime = convert_string_date_to_datetime(end_at)
    start_at_as_datetime = convert_string_date_to_datetime(start_at)
    plant_hist = (
        db.query(Plant_Hist)
        .filter(
            Plant_Hist.plant_id == plant_id,
            Plant_Hist.added_at >= start_at_as_datetime,
            Plant_Hist.added_at <= end_at_as_datetime,
        )
        .order_by(Plant_Hist.added_at.desc())
        .all()
    )
    return plant_hist
