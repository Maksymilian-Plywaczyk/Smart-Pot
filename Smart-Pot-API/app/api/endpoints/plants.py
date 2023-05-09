from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.endpoints.tags import Tag
from app.core.dependencies import get_db
from app.crud.crud_plants import (
    create_new_plant,
    get_current_user_plants,
    get_plant_by_id,
    update_plant,
)
from app.crud.crud_users import get_current_user
from app.models.user import User
from app.schemas.plant import Plant, PlantCreate, PlantUpdate

router = APIRouter(prefix="/api/v1/plants", tags=[Tag.PLANTS])


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[Plant])
def get_current_user_plants(plants: Annotated[List, Depends(get_current_user_plants)]):
    return plants


@router.get("/{plant_id}", status_code=status.HTTP_200_OK, response_model=Plant)
def read_plant_by_id(plant_id: int, db: Session = Depends(get_db)) -> Plant:
    plant = get_plant_by_id(plant_id=plant_id, db=db)
    if plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find plant"
        )
    return plant


@router.post("/new-plant", status_code=status.HTTP_201_CREATED, response_model=Plant)
def create_new_plant_for_current_user(
    new_plant: PlantCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    new_plant = create_new_plant(new_plant, db, current_user.id)
    return new_plant


@router.patch("/{plant_id}", status_code=status.HTTP_200_OK, response_model=Plant)
def update_existing_plant(
    plant_id: int, updated_plant: PlantUpdate, db: Session = Depends(get_db)
):
    updated_plant = update_plant(plant_id, db, updated_plant)
    return updated_plant
