from typing import Optional

from fastapi import APIRouter, HTTPException, Response, Depends

from app.basket.dao import BasketDAO
from app.exception.base_exceptions import DataBaseError
from app.exception.user_exceptions import UserNotFound, InvalidPasswordError
from app.user.auth import get_password_hash, create_access_token
from app.user.dao import UserDAO
from app.user.dependencies import authenticate_user, get_current_user
from app.database.models.user_model import User
from app.user.schemas import UserCreate, UserBase, UserRead

router_auth = APIRouter(prefix="/auth", tags=["Auth"])

router_user = APIRouter(prefix="/user", tags=["Пользователь"])


@router_auth.post("/register")
async def register_user(user_data: UserCreate):
    """
    Эта функция обрабатывает запрос на регистрацию нового пользователя.
    Хэширует пароль и добавляет нового пользователя в базу данных.
    Также создается корзина для нового пользователя.
    """

    # Проверяем, существует ли пользователь с указанным email в базе данных
    existing_user = await UserDAO.find_one_or_none(email=user_data.email)

    # Если пользователь с таким email уже зарегистрирован, возвращаем ошибку 409
    if existing_user:
        raise HTTPException(status_code=409, detail="Пользователь уже зарегистрирован")

    try:
        # Хэшируем пароль пользователя
        hash_password = get_password_hash(user_data.password)

        # Добавляем нового пользователя в базу данных
        new_user = await UserDAO.add(email=user_data.email, hash_password=hash_password)

        # При регистрации нового пользователя создаем корзину для него
        basket_user = await BasketDAO.add(user_id=new_user["id"])

        # Возвращаем объект нового пользователя
        return new_user

    # Обрабатываем ошибки, связанные с базой данных
    except DataBaseError:
        raise HTTPException(status_code=500, detail="Ошибка базы данных")


@router_auth.post("/login")
async def login_user(response: Response, user_data: UserCreate):
    """
    Эта функция обрабатывает запрос на вход пользователя.
    Она проверяет правильность email и пароля, а затем создает и сохраняет
    JWT-токен в cookies ответа.
    """

    try:
        # Аутентифицируем пользователя по email и паролю
        user = await authenticate_user(user_data.email, user_data.password)

        # Создаем JWT-токен с информацией о пользователе
        access_token = create_access_token({"sub": str(user.id)})

        # Устанавливаем токен в cookies, делая его доступным только через HTTP
        response.set_cookie("access_token", access_token, httponly=True)

        # Возвращаем сообщение о статусе авторизации
        return {"status": "Пользователь авторизован"}

        # Обрабатываем случай, когда пользователь не найден
    except UserNotFound:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обрабатываем случай, когда пароль неверен
    except InvalidPasswordError:
        raise HTTPException(status_code=401, detail="Пароль не верный")


@router_auth.post("/logout")
async def logout_user(response: Response) -> dict:
    """
    Эта функция обрабатывает запрос на выход пользователя.
    Она удаляет JWT-токен из cookies, тем самым деавторизуя пользователя.
    """

    # Удаляем cookie с токеном, чтобы деавторизовать пользователя
    response.delete_cookie("access_token")

    # Возвращаем сообщение о статусе деавторизации
    return {"status": "Пользователь деавторизован"}


@router_user.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> UserBase:
    return current_user


@router_user.patch("/change_password")
async def update_data_user(
    password: str, user: UserRead = Depends(get_current_user)
) -> Optional[UserBase]:
    """
    Эта функция позволяет пользователю изменить свой пароль. Новый пароль
    хэшируется и сохраняется в базе данных.
    """

    # Хэшируем новый пароль
    hash_password = get_password_hash(password)

    # Обновляем данные пользователя в базе данных, сохраняя новый хэшированный пароль
    new_data = await UserDAO.update(user.id, hash_password=hash_password)

    # Возвращаем обновленный объект пользователя или None, если пользователь не найден
    return await UserDAO.find_one_or_none(id=new_data["id"])
