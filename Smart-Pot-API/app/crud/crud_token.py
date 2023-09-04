from sqlalchemy.orm import Session

from app.models.blacklist_token import BlackListToken


def get_token_by_token(db: Session, token: str):
    return db.query(BlackListToken).filter(BlackListToken.token == token).first()
