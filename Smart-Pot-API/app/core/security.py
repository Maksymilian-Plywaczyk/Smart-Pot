import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..core.settings import settings
from ..crud.crud_token import get_token_by_token
from ..models.blacklist_token import BlackListToken
from ..models.user import User
from ..schemas.message import Message

SECRET_KEY = settings.SECRET_KEY  # secret key for JWT
ALGORITHM = "HS256"  # type of algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = (
    settings.ACCESS_TOKEN_EXPIRE_MINUTES
)  # expire time for access token

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def get_hashed_password(plain_password: str) -> str:
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def verify_device_token(device_token_db: str, request_device_token: str) -> bool:
    if device_token_db == request_device_token:
        return True
    return False


def verify_device_name_with_updated_name(device_in: str, device_updated) -> bool:
    if device_in == device_updated:
        return True
    return False


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    expires_delta_time: datetime
    if expires_delta is not None:
        expires_delta_time = datetime.utcnow() + expires_delta
    else:
        expires_delta_time = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta_time, "subject": str(subject)}
    if SECRET_KEY is not None:
        encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    else:
        raise ValueError("SECRET_KEY must be set")


def create_reset_password_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    expires_delta_time: datetime
    if expires_delta is not None:
        expires_delta_time = datetime.utcnow() + expires_delta
    else:
        expires_delta_time = datetime.utcnow() + timedelta(
            minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_TIME
        )
    to_encode = {"exp": expires_delta_time, "subject": str(subject)}
    if SECRET_KEY is not None:
        encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    else:
        raise ValueError("SECRET_KEY must be set")


def create_refresh_token(subject: Union[str, Any]) -> str:
    expires_delta = datetime.utcnow() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_TIME
    )
    to_encode = {"exp": expires_delta, "subject": str(subject)}
    if SECRET_KEY is not None:
        encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    else:
        raise ValueError("SECRET_KEY must be set")


def destroy_access_token(db: Session, token: str, current_user: User) -> Message:
    current_user_email = verify_access_token(token)
    try:
        if current_user_email == current_user.email:
            if get_token_by_token(db, token):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token already in blacklist",
                )
            invalidate_at = datetime.utcnow()
            db_token = BlackListToken(token=token, invalidated_at=invalidate_at)
            db.add(db_token)
            db.commit()
            return Message(message="Token destroyed successfully")
        else:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to destroy this token.",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Token has already expired.",
        )


def create_device_token(length_token: int) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length_token))


def verify_access_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["subject"]
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError
    except jwt.JWTError:
        raise jwt.JWTError
