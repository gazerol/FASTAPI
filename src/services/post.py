import json
from jwt import encode
from typing import Optional
from datetime import datetime
from functools import lru_cache
from fastapi import Depends
from sqlmodel import Session

from src.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TIME
from src.api.v1.schemas import PostCreate, PostModel
from src.db import AbstractCache, get_cache, get_session
from src.models import Post, User
from src.services import ServiceMixin

__all__ = ("PostService", "get_post_service")


class PostService(ServiceMixin):
    def get_post_list(self) -> dict:
        """Получить список постов."""
        posts = self.session.query(Post).order_by(Post.created_at).all()
        return {"posts": [PostModel(**post.dict()) for post in posts]}

    def get_post_detail(self, item_id: int) -> Optional[dict]:
        """Получить детальную информацию поста."""
        cached_post = self.cache.get(key=f"{item_id}")
        if cached_post:
            return json.loads(cached_post)

        post = self.session.query(Post).filter(Post.id == item_id).first()
        if post:
            self.cache.set(key=f"{post.id}", value=post.json())
        return post.dict() if post else None

    def create_post(self, post: PostCreate) -> dict:
        """Создать пост."""
        user = self.session.query(User).get(post.id)
        if user is None or user.last_login + JWT_ACCESS_TIME < int(datetime.utcnow().timestamp()):
            return dict()
        if post.accessToken != encode(
                {"username": user.username, "time": user.last_login},
                JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        ):
            return dict()
        new_post = Post(title=post.title, description=post.description, created_by=user.username)
        self.session.add(new_post)
        self.session.commit()
        self.session.refresh(new_post)
        return new_post.dict()


# get_post_service — это провайдер PostService. Синглтон
@lru_cache()
def get_post_service(
    cache: AbstractCache = Depends(get_cache),
    session: Session = Depends(get_session),
) -> PostService:
    return PostService(cache=cache, session=session)
