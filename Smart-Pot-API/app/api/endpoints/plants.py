from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.api.endpoints.tags import Tag
from app.crud.crud_plants import get_current_user_plants

router = APIRouter(prefix="/api/v1/plants", tags=[Tag.PLANTS])


@router.get("/")
def get_current_user_plants(plants: Annotated[List, Depends(get_current_user_plants)]):
    return plants
