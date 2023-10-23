from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..crud.crud_plants import get_user_plant_by_id
from ..crud.crud_users import get_current_active_user
from ..models.sensor_threshold import SensorThreshold as SensorThresholdModel
from ..models.user import User
from ..schemas.sensor_threshold import SensorThresholdUpdate


def get_sensor_threshold_by_id(
    db: Session, sensor_threshold_id: str, plant_id: int
) -> Any:
    sensor_threshold_by_id = (
        db.query(SensorThresholdModel)
        .filter(
            SensorThresholdModel.threshold_id == sensor_threshold_id,
            SensorThresholdModel.plant_id == plant_id,
        )
        .first()
    )
    return sensor_threshold_by_id


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


def update_user_sensor_threshold(
    db: Session,
    update_threshold_sensor: SensorThresholdUpdate,
    plant_id: int,
    user_id: int,
) -> Any:
    user_plant = get_user_plant_by_id(db, plant_id, user_id)
    if not user_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} has not plant with id {plant_id}",
        )
    db_threshold = get_sensor_threshold_by_id(
        db, update_threshold_sensor.threshold_id, plant_id
    )
    if not db_threshold:
        new_threshold = SensorThresholdModel(
            **update_threshold_sensor.dict(), plant_id=plant_id
        )
        db.add(new_threshold)
        db.commit()
        db.refresh(new_threshold)
        return new_threshold
    else:
        threshold_data = update_threshold_sensor.dict(exclude_unset=True)
        for key, value in threshold_data.items():
            setattr(db_threshold, key, value)
        db.add(db_threshold)
        db.commit()
        db.refresh(db_threshold)
    return db_threshold
