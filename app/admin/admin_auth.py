from typing import Optional

from jose import jwt
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.config import settings
from app.user.auth import create_access_token
from app.user.dependencies import authenticate_user, get_current_user


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # Извлекаем данные формы (имя пользователя и пароль) из запроса
        form = await request.form()
        email, password = form.get("username"), form.get("password")

        # Пытаемся аутентифицировать пользователя с помощью функции authenticate_user
        user = await authenticate_user(email, password)

        if user:
            # Если пользователь найден, создаем JWT-токен с ID и email пользователя
            access_token = create_access_token({"sub": str(user.id), "email": email})

            # Проверяем, является ли пользователь администратором
            if jwt.decode(access_token, settings.SECRET_KEY)["role"] == "admin":
                # Если пользователь администратор, сохраняем токен в сессии
                request.session.update({"token": access_token})

        # Возвращаем True вне зависимости от успеха аутентификации
        return True

    async def logout(self, request: Request) -> bool:
        # Очищаем сессию пользователя, удаляя все сохраненные данные
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        # Извлекаем токен из сессии
        token = request.session.get("token")

        # Если токен отсутствует, перенаправляем пользователя на страницу входа
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        # Проверяем токен и извлекаем пользователя
        user = await get_current_user(token)

        # Если пользователь не найден или токен недействителен, перенаправляем на страницу входа
        if not user:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        # Если все в порядке, возвращаем True
        return True


authentication_backend = AdminAuth(secret_key="...")
