import re
from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from pydantic import ConfigDict, field_validator

from .base import Base


class _User(Base):
    username: str
    email: str


class User(_User):
    id: UUID
    disabled: bool = False
    pass


class UserRegistration(_User):
    password: str

    @field_validator('username', mode='before')
    @classmethod
    def check_len(cls, value: str):
        if not (3 <= len(value) <= 32):
            raise ValueError('username length must be between 3 and 32')
        if re.search(pattern=r'[^a-zA-Z0-9_\.]', string=value):
            raise ValueError('only characters a-Z, 0-9, . and _ are allowed')
        return value

    @field_validator('username', mode='before')
    @classmethod
    def check_symbol(cls, value: str):
        if not (3 <= len(value) <= 32):
            raise ValueError('username length must be between 3 and 32')
        if re.search(pattern=r'[^a-zA-Z0-9_\.]', string=value):
            raise ValueError('only characters a-Z, 0-9, . and _ are allowed')
        return value

    @field_validator('email', mode='before')
    @classmethod
    def is_email(cls, value: str):
        try:
            # Check that the email address is valid. Turn on check_deliverability
            # for first-time validations like on account creation pages (but not
            # login pages).
            email_info = validate_email(value, check_deliverability=False)

            # After this point, use only the normalized form of the email address,
            # especially before going to a database query.
            email = email_info.normalized

        except EmailNotValidError:
            # The exception message is human-readable explanation of why it's
            # not a valid (or deliverable) email address.
            raise ValueError('email is not a correct email address')
        return email.lower()

    @field_validator('password', mode='before')
    @classmethod
    def strong_password(cls, value: str):
        # TODO check
        if not (8 <= len(value) <= 132):
            raise ValueError('password length must be between 8 and 128')

        if not (re.search(pattern=r'[a-z]', string=value) and re.search(pattern=r'[A-Z]', string=value) and re.search(
                pattern=r'[0-9]', string=value) and re.search(pattern=r'[^a-zA-Z0-9]', string=value)):
            raise ValueError('password does not meet security requirements')
        return value


class UserInDB(_User):
    id: UUID
    psw_hash: str
    model_config = ConfigDict(from_attributes=True)
