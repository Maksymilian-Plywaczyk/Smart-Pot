from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_plants import get_user_plant_by_id
from app.crud.crud_users import get_current_active_user
from app.models.sensor_threshold import SensorThreshold as SensorThresholdModel
from app.models.user import User
from app.schemas.sensor_threshold import SensorThresholdCreate, SensorThresholdUpdate


def get_sensor_threshold_by_id(db: Session, sensor_threshold_id: int) -> Any:
    sensor_threshold_by_id = (
        db.query(SensorThresholdModel)
        .filter(SensorThresholdModel.id == sensor_threshold_id)
        .first()
    )
    return sensor_threshold_by_id


def get_user_sensor_by_name(db: Session, sensor_name: str, plant_id: int) -> Any:
    sensor_by_name = (
        db.query(SensorThresholdModel)
        .filter(
            SensorThresholdModel.sensor_name == sensor_name,
            SensorThresholdModel.plant_id == plant_id,
        )
        .first()
    )
    return sensor_by_name


def get_current_user_sensor_thresholds(
    current_active_user: Annotated[User, Depends(get_current_active_user)]
):
    if not current_active_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or user is not active",
        )
    sensor_thresholds = []
    for plant in current_active_user.plants:
        sensor_thresholds.append(plant.sensor_threshold)

    return sensor_thresholds


def create_new_sensor_threshold(
    db: Session,
    new_threshold_sensor: SensorThresholdCreate,
    plant_id: int,
    user_id: int,
) -> Any:
    user_plant = get_user_plant_by_id(db, plant_id, user_id)
    if not user_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} has not plant with id {plant_id}",
        )
    if get_user_sensor_by_name(db, new_threshold_sensor.sensor_name, plant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plant {plant_id} already has sensor "
            f"{new_threshold_sensor.sensor_name}",
        )
    new_threshold_sensor = SensorThresholdModel(
        **new_threshold_sensor.dict(), plant_id=plant_id
    )
    db.add(new_threshold_sensor)
    db.commit()
    db.refresh(new_threshold_sensor)
    return new_threshold_sensor


def update_user_sensor_threshold(
    db: Session,
    update_threshold_sensor: SensorThresholdUpdate,
    plant_id: int,
    user_id: int,
    threshold_id: int,
) -> Any:
    user_plant = get_user_plant_by_id(db, plant_id, user_id)
    if not user_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} has not plant with id {plant_id}",
        )
    db_threshold = get_sensor_threshold_by_id(db, threshold_id)
    if not db_threshold:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plant {plant_id} has not sensor "
            f"{update_threshold_sensor.sensor_name}",
        )

    threshold_data = update_threshold_sensor.dict(exclude_unset=True)
    for key, value in threshold_data.items():
        setattr(db_threshold, key, value)
    db.add(db_threshold)
    db.commit()
    db.refresh(db_threshold)
    return db_threshold


def delete_user_sensor_threshold(db: Session, threshold_id: int) -> Any:
    db_threshold = get_sensor_threshold_by_id(db, threshold_id)
    if not db_threshold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot find threshold with id {threshold_id}",
        )
    db.delete(db_threshold)
    db.commit()
    return db_threshold
