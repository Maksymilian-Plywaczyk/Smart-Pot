from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import (
    get_hashed_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
)
from app.crud.crud_token import get_token_by_token
from app.models.user import User
from app.schemas.token import TokenPayload
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, user_email: str):
    user_by_email = db.query(User).filter(User.email == user_email).first()
    return user_by_email


def user_authentication(db: Session, user_email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db=db, user_email=user_email)
    if not user:
        return None
    if not verify_password(password, hashed_password=user.hashed_password):
        return None
    return user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_expire_exception = HTTPException(
        status_code=401,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = verify_access_token(token)
        if get_token_by_token(db=db, token=token):
            raise HTTPException(
                status_code=401,
                detail="Token is invalid or has been invalidated (logged out).",
            )
        if email is None:
            raise credentials_exception
        token_data = TokenPayload(email=email)
    except jwt.ExpiredSignatureError:
        raise token_expire_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db=db, user_email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def is_active(user: User) -> bool:
    if not user.is_active:
        return False
    return True


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_new_user(db: Session, user: UserCreate):
    hashed_password = get_hashed_password(plain_password=user.password)
    database_user = User(
        full_name=user.full_name, email=user.email, hashed_password=hashed_password
    )
    db.add(database_user)
    db.commit()
    db.refresh(database_user)
    return database_user
