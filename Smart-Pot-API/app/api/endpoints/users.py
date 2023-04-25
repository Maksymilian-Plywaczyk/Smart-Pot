from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.endpoints.tags import Tag
from app.crud.crud_users import get_current_active_user
from app.schemas.user import User

router = APIRouter(prefix="/api/v1/users", tags=[Tag.LOGIN])


@router.get("/me", response_model=User)
def get_current_user(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
