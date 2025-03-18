from pydantic import BaseModel, EmailStr, constr, Field
from typing import Annotated
from config import PASSWORD_REGEX


class UserCreate(BaseModel):
    email: EmailStr
    password: Annotated[
        str,
        Field(
            min_length=8,
            pattern=PASSWORD_REGEX,
            description="Password must contain at least one letter and one number.",
        ),
    ]


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str


class PostCreate(BaseModel):
    text: Annotated[str, constr(min_length=1, max_length=1048576)]


class PostResponse(BaseModel):
    id: int
    text: str
    owner_id: int

    class Config:
        from_attributes = True
