from sqlalchemy.orm import Session

from app.models.plant import Plant


def get_plant_by_id(db: Session, plant_id: int):
    plant_by_id = db.query(Plant).filter(Plant.plant_id == plant_id).first()
    return plant_by_id
