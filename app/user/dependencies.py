from fastapi import HTTPException, Depends, Request
from jose import jwt, ExpiredSignatureError, JWTError
from pydantic import EmailStr

from app.config import settings
from app.exception.user_exceptions import (
    UserNotFound,
    InvalidPasswordError,
    TokenNotFound,
)
from app.user.auth import verify_password
from app.user.dao import UserDAO


async def authenticate_user(email: EmailStr, password: str):
    """
    Аутентификация пользователя.

    Проверяет наличие пользователя с указанным email и соответствие пароля.
    """

    # Ищем пользователя по email в базе данных
    user = await UserDAO.find_one_or_none(email=email)

    # Если пользователь не найден, выбрасываем исключение UserNotFound
    if not user:
        raise UserNotFound
    else:
        # Проверяем соответствие переданного пароля хэшированному паролю пользователя
        if not verify_password(password, user.hash_password):
            # Если пароли не совпадают, выбрасываем исключение InvalidPasswordError
            raise InvalidPasswordError

    # Возвращаем объект пользователя, если аутентификация успешна
    return user


def get_token(request: Request):
    """Извлечение токена из cookies запроса."""

    # Извлечение токена из cookies с ключом "access_token"
    token = request.cookies.get("access_token")

    # Если токен отсутствует, выбрасываем исключение с кодом 404
    if not token:
        raise HTTPException(status_code=404, detail="Пользователь не аутентифицирован")

    # Возвращаем извлеченный токен
    return token


async def get_current_user(token: str = Depends(get_token)):
    """
    Получает текущего пользователя по JWT-токену.

    Декодирует токен, проверяет его валидность и извлекает ID пользователя.
    Если токен недействителен или пользователь не найден, выбрасывает HTTPException.
    """
    try:
        # Декодируем токен с использованием секретного ключа и алгоритма
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)

        # Обработка случаев, когда токен не найден
    except TokenNotFound:
        raise HTTPException(status_code=404, detail="Токен пользователя не найден")

        # Обработка случаев, когда срок действия токена истек
    except ExpiredSignatureError:
        raise HTTPException(status_code=500, detail="Срок действия токена истек.")

        # Обработка других ошибок при работе с JWT
    except JWTError:
        raise HTTPException(status_code=401, detail="Произошла непредвиденная ошибка.")

        # Извлекаем идентификатор пользователя из payload и ищем пользователя в базе данных
    user = await UserDAO.find_one_or_none(id=int(payload.get("sub")))

    # Если пользователь не найден, возвращаем ошибку 404
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    # Возвращаем объект пользователя
    return user
