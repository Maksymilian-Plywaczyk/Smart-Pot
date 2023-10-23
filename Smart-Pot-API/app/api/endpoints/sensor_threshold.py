from typing import Annotated, List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.endpoints.tags import Tag
from ...core.dependencies import get_db
from ...crud.crud_sensor_treshold import (
    get_current_user_sensor_thresholds,
    get_sensor_threshold_by_id,
    update_user_sensor_threshold,
)
from ...crud.crud_users import get_current_active_user
from ...models.user import User
from ...schemas.sensor_threshold import SensorThreshold, SensorThresholdUpdate

router = APIRouter(prefix="/api/v1/sensor-threshold", tags=[Tag.THRESHOLDS])


@router.get(
    "/get-current-user-thresholds",
    status_code=status.HTTP_200_OK,
    response_model=List[List[Union[SensorThreshold, None]]],
)
def get_current_user_thresholds(
    thresholds: Annotated[List, Depends(get_current_user_sensor_thresholds)]
):
    return thresholds


@router.get(
    "/get-threshold/{plant_id}/{threshold_id}",
    status_code=status.HTTP_200_OK,
    response_model=SensorThreshold,
)
def get_user_threshold_by_id(
    plant_id: int,
    threshold_id: str,
    current_active_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if not current_active_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or user is not active",
        )
    sensor_threshold = get_sensor_threshold_by_id(db, threshold_id, plant_id)
    if sensor_threshold is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find threshold"
        )
    return sensor_threshold


@router.put(
    "/update-threshold/{plant_id}",
    status_code=status.HTTP_200_OK,
    response_model=SensorThreshold,
)
def update_threshold(
    plant_id: int,
    update_threshold_sensor: SensorThresholdUpdate,
    current_active_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if not current_active_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or user is not active",
        )
    updated_threshold = update_user_sensor_threshold(
        db, update_threshold_sensor, plant_id, current_active_user.id
    )
    print(updated_threshold)
    return updated_threshold
