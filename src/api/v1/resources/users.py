from starlette import status
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import UserCreate, UserModel, UserLogin
from src.api.v1.schemas import Token, CheckProfile, ChangeProfile, UserToken, RefreshToken
from src.services import UserService, get_user_service


router = APIRouter()


@router.post(
    path="/signup",
    summary="Регистрация пользователя",
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def user_create(
        user: UserCreate,
        user_service: UserService = Depends(get_user_service),
) -> dict:
    return user_service.create_user(user=user)


@router.post(
    path="/login",
    summary="Авторизация",
    response_model=Token,
    tags=["users"],
)
def user_login(
    user: UserLogin, user_service: UserService = Depends(get_user_service),
) -> Token:
    """User authorization"""
    token: dict = user_service.login_user(user)
    return Token(**token)


@router.post(
    path="/refresh",
    summary="Обновление токена",
    response_model=Token,
    tags=["users"],
)
def user_refresh(
    refresh_token: RefreshToken, user_service: UserService = Depends(get_user_service),
) -> Token:
    """Token Update"""
    token: dict = user_service.refresh(refresh_token)
    if token == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Check id or refresh token")
    return Token(**token)


@router.post(
    path="/users/me",
    summary="Информация о пользователе",
    response_model=UserModel,
    tags=["users"],
)
def user_profile(
    user: CheckProfile, user_service: UserService = Depends(get_user_service),
) -> UserModel:
    """User Information"""
    profile: dict = user_service.check_profile(user)
    if profile == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Check access token")
    return UserModel(**profile)


@router.put(
    path="/users/me",
    summary="Изменение информации о пользователе",
    response_model=UserToken,
    tags=["users"],
)
def change_profile(
    change: ChangeProfile, user_service: UserService = Depends(get_user_service),
) -> UserToken:
    """Changing User Information"""
    new_profile: dict = user_service.change_profile(change)
    if new_profile == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Check access token or username")
    return UserToken(**new_profile)



