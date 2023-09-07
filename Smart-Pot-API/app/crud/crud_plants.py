from typing import Annotated, Any, List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_device_token
from app.crud.crud_devices import get_device_by_id
from app.crud.crud_users import get_current_active_user, get_user_by_email
from app.models.plant import Plant as PlantDB
from app.models.user import User

from ..schemas.plant import Plant, PlantCreate, PlantUpdate


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


def update_plant(db: Session, updated_plant: PlantUpdate) -> Plant:
    db_device = get_device_by_id(db, updated_plant.device_id)
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User cannot update plant with not exisiting device",
        )
    db_plant = get_plant_by_device_id(db, plant_device_id=updated_plant.device_id)
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
    db.delete(db_plant)
    db.commit()
    return {"message": "Plant deleted successfully"}
