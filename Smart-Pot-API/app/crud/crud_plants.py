from typing import Annotated, List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_users import get_current_user
from app.models.plant import Plant as PlantDB
from app.models.user import User

from ..schemas.plant import Plant, PlantCreate, PlantUpdate


def get_plant_by_id(db: Session, plant_id: int):
    plant_by_id = db.query(PlantDB).filter(PlantDB.id == plant_id).first()
    return plant_by_id


def get_current_user_plants(
    current_user: Annotated[User, Depends(get_current_user)]
) -> List[Plant]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return current_user.plants


def create_new_plant(new_plant: PlantCreate, db: Session, user_id: int):
    database_plant = PlantDB(
        name=new_plant.name,
        humidity=new_plant.sensors.humidity,
        lux=new_plant.sensors.lux,
        temperature=new_plant.sensors.temperature,
        user_id=user_id,
    )
    db.add(database_plant)
    db.commit()
    db.refresh(database_plant)
    return database_plant


def update_plant(plant_id: int, db: Session, updated_plant: PlantUpdate) -> Plant:
    db_plant = get_plant_by_id(db, plant_id)
    if not db_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found"
        )
    plant_data = updated_plant.dict(exclude_unset=True)

    for key, value in plant_data.items():
        setattr(db_plant, key, value)
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant
