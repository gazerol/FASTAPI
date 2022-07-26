from datetime import datetime

from pydantic import BaseModel

__all__ = (
    "PostModel",
    "PostCreate",
    "PostListResponse",
)


class PostBase(BaseModel):
    title: str
    description: str


class PostCreate(PostBase):
    id: int = 0
    accessToken: str = ""


class PostModel(PostBase):
    id: int
    created_at: datetime
    created_by: str = ""


class PostListResponse(BaseModel):
    posts: list = []
