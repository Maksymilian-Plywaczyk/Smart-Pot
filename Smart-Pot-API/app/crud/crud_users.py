from typing import Annotated, Any, Optional

import pytz
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..core.dependencies import get_db
from ..core.security import (
    get_hashed_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
)
from ..crud.crud_token import get_token_by_token
from ..models.user import User
from ..schemas.token import TokenPayload
from ..schemas.user import UserCreate
from ..schemas.utils.languages import Languages


def validate_user_timezone(timezone: str) -> bool:
    if isinstance(timezone, str):
        timezone = timezone.strip().replace(" ", "_")
    else:
        return False
    try:
        pytz.timezone(timezone)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False


def get_user_by_email(db: Session, user_email: str):
    if isinstance(user_email, str):
        user_by_email = db.query(User).filter(User.email == user_email).first()
        return user_by_email
    return None


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


def update_user_timezone(db: Session, user: User, timezone: str) -> Any:
    if isinstance(user, User) is False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User not correctly provided")
    if not validate_user_timezone(timezone):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "User provide invalid timezone"
        )
    user.timezone = timezone
    db.commit()
    db.refresh(user)
    return user


def update_user_language(db: Session, user: User, language: str) -> Any:
    language_options = [language.value for language in Languages]
    if language not in language_options:
        raise ValueError(f"Language {language} is not supported")
    user.language = language
    db.commit()
    db.refresh(user)
    return user


def control_user_activity(db: Session, user: User, state: bool) -> Any:
    if isinstance(user, User) is False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User not correctly provided")
    user.is_active = state
    db.commit()
    db.refresh(user)
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_new_user(db: Session, user: UserCreate):
    if not user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "User need to provide necessary data"
        )
    hashed_password = get_hashed_password(plain_password=user.password)
    database_user = User(
        full_name=user.full_name, email=user.email, hashed_password=hashed_password
    )
    db.add(database_user)
    db.commit()
    db.refresh(database_user)
    return database_user


def delete_user(db: Session, user: User) -> Any:
    if isinstance(user, User) is False:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Cannot delete user, which is not correctly provided",
        )
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
