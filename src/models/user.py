from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

__all__ = ("User",)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(default="", nullable=False)
    email: str = Field(default="", nullable=False)
    password: str = Field(default="")
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    role: str = Field(default="user")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    last_login: int = Field(default=0)
    expires_in: int = Field(default=0)
