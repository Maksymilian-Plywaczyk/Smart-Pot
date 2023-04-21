from app.core.settings import settings
from passlib.context import CryptContext
from typing import Union, Optional
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = settings.SECRET_KEY  # secret key for JWT
ALGORITHM = "HS256"  # type of algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # expire time for access token

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def get_hashed_password(plain_password: str) -> str:
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "subject": str(subject)}
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["subject"]
    except jwt.JWTError:
        return None
