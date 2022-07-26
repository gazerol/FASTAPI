from datetime import datetime

from pydantic import BaseModel

__all__ = (
    "UserModel",
    "UserCreate",
    "Token",
    "UserLogin",
    "RefreshToken",
    "CheckProfile",
    "UserToken",
    "ChangeProfile",
)


class UserBase(BaseModel):
    username: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    password: str


class UserModel(UserBase):
    id: int
    created_at: datetime
    role: str
    is_superuser: bool
    is_active: bool


class Token(BaseModel):
    accessToken: str = ""
    refreshToken: str = ""
    expires_in: int = 0


class RefreshToken(BaseModel):
    id: int = 0
    refreshToken: str = ""


class CheckProfile(BaseModel):
    id: int = 0
    accessToken: str = ""


class ChangeProfile(BaseModel):
    id: int
    accessToken: str
    new_username: str
    new_email: str
    new_password: str


class UserToken(UserModel, Token):
    ...




