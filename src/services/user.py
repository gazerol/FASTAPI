from jwt import encode
from functools import lru_cache
from datetime import datetime
from fastapi import Depends
from sqlmodel import Session
from werkzeug.security import generate_password_hash, check_password_hash

from src.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TIME, JWT_REFRESH_TIME
from src.api.v1.schemas import UserCreate, UserModel, UserLogin
from src.api.v1.schemas import Token, CheckProfile, ChangeProfile, UserToken, RefreshToken
from src.db import AbstractCache, get_cache, get_session
from src.models import User
from src.services import ServiceMixin

__all__ = ("UserService", "get_user_service")


class UserService(ServiceMixin):
   
    def create_user(self, user: UserCreate) -> dict:
        """Create user"""
        new_user = User(
            username=user.username,
            password=generate_password_hash(user.password, method="sha256"),
            email=user.email
        )
        if self.session.query(User).filter(User.username == new_user.username).first():
            return {"error": "User already exists."}
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return {"msg": "User create.", "user": new_user}

    def login_user(self, user: UserLogin) -> dict:
        """Login user"""
        check_user = (self.session.query(User).filter(User.username == user.username).first())
        if not check_user:
            return {"error": "User not found."}
        if not check_password_hash(check_user.password, user.password):
            return {"error": "Wrong password"}

        token = Token()
        time = int(datetime.utcnow().timestamp())
        token.accessToken = encode(
            {"username": check_user.username, "time": time},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM,
        )
        token.refreshToken = encode(
            {"id": check_user.id, "time": time},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM,
        )

        check_user.last_login = time
        self.session.add(check_user)
        self.session.commit()
        token.expires_in = time + JWT_ACCESS_TIME
        check_user.expires_in = time + JWT_REFRESH_TIME
        self.session.add(check_user)
        self.session.commit()
        return token.dict()

#

    def refresh(self, refresh_token: RefreshToken) -> dict:
        """Update token"""
        user = self.session.query(User).get(refresh_token.id)
        if user is None or user.expires_in < int(datetime.utcnow().timestamp()):
            return dict()
        if refresh_token.refreshToken != encode(
                {"id": user.id, "time": user.last_login},
                JWT_SECRET_KEY, algorithm=JWT_ALGORITHM):
            return dict()
        token = Token()
        time = int(datetime.utcnow().timestamp())
        token.accessToken = encode(
            {"username": user.username, "time": time},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        )
        token.refreshToken = encode(
            {"id": user.id, "time": time},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        )

        user.last_login = time
        token.expires_in = time + JWT_ACCESS_TIME
        user.expires_in = time + JWT_REFRESH_TIME
        self.session.add(user)
        self.session.commit()
        return token.dict()
#

    def check_profile(self, user: CheckProfile) -> dict:
        """Viewing a profile"""
        profile = self.session.query(User).get(user.id)
        if profile is None or profile.last_login + JWT_ACCESS_TIME < int(datetime.utcnow().timestamp()):
            return dict()
        if user.accessToken != encode(
                {"username": profile.username, "time": profile.last_login},
                JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        ):
            return dict()
        return profile.dict()
#

    def change_profile(self, change: ChangeProfile) -> dict:
        """change a profile"""
        profile = self.session.query(User).get(change.id)
        if profile is None or profile.last_login + JWT_ACCESS_TIME < int(datetime.utcnow().timestamp()):
            return dict()
        if change.accessToken != encode(
                {"username": profile.username, "time": profile.last_login},
                JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        ):
            return dict()
        profile.email = change.new_email
        profile.username = change.new_username
        profile.password = generate_password_hash(change.new_password, method="sha256")
        time = int(datetime.utcnow().timestamp())
        profile.last_login = time
        profile.expires_in = time + JWT_REFRESH_TIME
        self.session.add(profile)
        self.session.commit()
        user_token = UserToken(
            id=profile.id, username=profile.username,
            created_at=profile.created_at, role=profile.role,
            is_superuser=profile.is_superuser, is_active=profile.is_active,
            email=profile.email
        )
        user_token.accessToken = encode(
            {"username": profile.username, "time": time},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        )
        user_token.refreshToken = encode(
            {"id": profile.id, "time": time},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        )
        user_token.expires_in = time + JWT_ACCESS_TIME
        return user_token.dict()


# get_post_service — это провайдер PostService. Синглтон
@lru_cache()
def get_user_service(
    cache: AbstractCache = Depends(get_cache),
    session: Session = Depends(get_session),
) -> UserService:
    return UserService(cache=cache, session=session)
