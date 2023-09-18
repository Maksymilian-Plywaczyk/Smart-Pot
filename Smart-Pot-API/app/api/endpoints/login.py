from datetime import timedelta
from typing import Annotated, Any, Union

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.endpoints.tags import Tag
from app.core.dependencies import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_password_token,
    destroy_access_token,
    get_hashed_password,
    oauth2_scheme,
    verify_access_token,
)
from app.core.settings import settings
from app.crud.crud_users import (
    create_new_user,
    get_current_user,
    get_user_by_email,
    is_active,
    user_authentication,
)
from app.crud.email_connection import MailConnection
from app.models.user import User
from app.schemas.mail import Email
from app.schemas.message import Message
from app.schemas.token import RefreshToken, ResetToken, Token
from app.schemas.user import UserCreate

router = APIRouter(prefix="/api/v1", tags=[Tag.LOGIN])


class OAuth2PasswordRequestJson:
    def __init__(self, email: str = Body(), password: str = Body()):
        self.username = email
        self.password = password


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
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.email)
    user.is_active = True
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", response_model=Message)
def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> Any:
    current_user.is_active = False
    db.commit()
    destroy_access_token(db=db, token=token, current_user=current_user)
    return {"message": "User logged out successfully"}


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


@router.post("/refresh", response_model=Token)
def get_refresh_token(
    refresh_token: RefreshToken, db: Session = Depends(get_db)
) -> Any:
    try:
        user_email = verify_access_token(refresh_token.token)
        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or has been invalidated (logged out).",
            )
        if not get_user_by_email(db=db, user_email=user_email):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    new_access_token = create_access_token(subject=user_email)
    new_refresh_token = create_refresh_token(subject=user_email)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/reset-password", response_model=Message)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
) -> Any:
    user_email = verify_access_token(token)
    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has been invalidated (logged out).",
        )
    user = get_user_by_email(db=db, user_email=user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )
    elif not is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is inactive",
        )
    hashed_password = get_hashed_password(new_password)
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}


@router.post("/recover-password", response_model=Union[None, ResetToken])
async def recover_password(
    user_email: EmailStr = Body(..., embed=True), db: Session = Depends(get_db)
) -> Any:
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )
    email_address = EmailStr(user_email)
    action_url = settings.FRONTEND_URL + "/reset-password"
    email = Email(
        email=email_address, body={"name": user.full_name, "action_url": action_url}
    )
    mail_connection = MailConnection(email)
    response = await mail_connection.send_email_resetting_password()
    token = create_reset_password_token(subject=user_email)
    if response.status_code == 200:
        return {"reset_password_token": token, "token_type": "bearer"}
    else:
        return None
