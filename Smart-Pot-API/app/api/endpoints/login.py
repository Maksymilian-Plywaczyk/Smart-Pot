from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.endpoints.tags import Tag
from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.core.settings import settings
from app.crud.crud_users import create_new_user, get_user_by_email, user_authentication
from app.schemas.message import Message
from app.schemas.token import Token
from app.schemas.user import UserCreate

router = APIRouter(prefix="/api/v1", tags=[Tag.LOGIN])


@router.post("/token", response_model=Token)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Any:
    user = user_authentication(
        db=db, user_email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": create_access_token(
            subject=user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/registration", response_model=Message)
def registration(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    new_user = get_user_by_email(db=db, user_email=user_in.email)
    if new_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist",
        )
    create_new_user(db=db, user=user_in)
    return {"message": "User created successfully"}
