from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.endpoints.tags import Tag
from app.core.dependencies import get_db
from app.crud.crud_plants import get_current_user_plants, get_plant_by_id
from app.schemas.plant import Plant

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
