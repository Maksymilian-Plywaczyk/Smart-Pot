from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.endpoints.tags import Tag
from ...core.dependencies import get_db
from ...core.security import verify_access_token
from ...crud.crud_users import (
    delete_user,
    get_current_active_user,
    update_user_language,
    update_user_timezone,
    user_authentication,
)
from ...schemas.message import Message
from ...schemas.user import User, UserDelete, UserTimezoneSet
from ...schemas.utils.languages import UpdateUserLanguage

router = APIRouter(prefix="/api/v1/users", tags=[Tag.USERS])


@router.get("/me", response_model=User)
def get_current_user(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.patch("/update-language", response_model=Message, status_code=200)
def update_active_user_language(
    current_active_user: Annotated[User, Depends(get_current_active_user)],
    language: UpdateUserLanguage,
    db: Session = Depends(get_db),
):
    if not current_active_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active"
        )
    user = update_user_language(
        db=db, user=current_active_user, language=language.language
    )
    return {"message": f"User language has been updated to {user.language}"}


@router.patch("/update-timezone", response_model=Message, status_code=200)
def update_active_user_timezone(
    current_active_user: Annotated[User, Depends(get_current_active_user)],
    timezone: UserTimezoneSet,
    db: Session = Depends(get_db),
):
    if not current_active_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active"
        )

    user = update_user_timezone(
        db=db, user=current_active_user, timezone=timezone.timezone
    )
    return {"message": f"User timezone has been updated to {user.timezone}"}


@router.delete("/active-user-delete", response_model=Message, status_code=200)
def delete_active_user(
    current_active_user: Annotated[User, Depends(get_current_active_user)],
    user_delete: UserDelete,
    db: Session = Depends(get_db),
):
    if not current_active_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active"
        )
    user_delete_email = verify_access_token(user_delete.user_token)
    if not user_delete_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect token"
        )
    if not user_authentication(
        db=db, user_email=current_active_user.email, password=user_delete.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User provide wrong password",
        )
    message = delete_user(db=db, user=current_active_user)
    return message
