from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional
from app.core.security import verify_password, get_hashed_password
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, user_email: str):
    user_by_email = db.query(User).filter(User.email == user_email).first()
    return user_by_email


def user_authentication(db: Session, user_email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db=db, user_email=user_email)
    if not user: return None
    if not verify_password(password, hashed_password=user.hashed_password): return None
    return user


def user_is_active(user: User) -> bool:
    return user.is_active


def create_new_user(db: Session, user: UserCreate):
    hashed_password = get_hashed_password(plain_password=user.password)
    database_user = User(full_name=user.full_name, email=user.email, hashed_password=hashed_password)
    db.add(database_user)
    db.commit()
    db.refresh(database_user)
    return database_user
