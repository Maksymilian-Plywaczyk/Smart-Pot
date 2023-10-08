from enum import Enum

from pydantic import BaseModel, validator


class Languages(str, Enum):
    POLISH: str = "PL"
    ENGLISH: str = "ENG"


class UpdateUserLanguage(BaseModel):
    language: Languages

    @validator("language")
    def validate_language(cls, value):
        language_options = [language.value for language in Languages]
        if value not in language_options:
            raise ValueError("Invalid language provided")
        return value
