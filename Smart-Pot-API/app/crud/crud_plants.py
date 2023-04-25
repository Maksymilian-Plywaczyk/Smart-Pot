from typing import Annotated, List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_users import get_current_user
from app.models.plant import Plant
from app.models.user import User


def get_plant_by_id(db: Session, plant_id: int):
    plant_by_id = db.query(Plant).filter(Plant.id == plant_id).first()
    return plant_by_id


def get_current_user_plants(
    current_user: Annotated[User, Depends(get_current_user)]
) -> List[Plant]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return current_user.plants
