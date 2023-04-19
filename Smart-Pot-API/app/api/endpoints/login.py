from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.endpoints.tags import Tag
from app.schemas.token import Token
from app.schemas.message import Message
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.crud.crud_users import user_authentication, user_is_active, create_new_user, get_user_by_email
from typing import Any
from app.core.settings import settings
from datetime import timedelta
from app.core.security import create_access_token

router = APIRouter(prefix="/api/v1", tags=[Tag.LOGIN])


@router.post("/login/access-token", response_model=Token)
def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = user_authentication(db=db, user_email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot find user")

    elif not user_is_active(user=user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {"access_token": create_access_token(subject=user.email, expires_delta=access_token_expires),
            "token_type": "bearer"}


@router.post("/registration", response_model=Message)
def registration(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    new_user = get_user_by_email(db=db, user_email=user_in.email)
    if new_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exist")
    create_new_user(db=db, user=user_in)
    return {"message": "User created successfully"}
