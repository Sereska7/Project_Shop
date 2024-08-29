from app.exception.base_exceptions import CustomError


class UserNotFound(CustomError):
    """Ошибка для случая, когда пользователь не найден."""

    pass


class InvalidPasswordError(CustomError):
    """Ошибка для случая, когда пароль не верный."""

    pass


class TokenNotFound(CustomError):
    """Ошибка для случая, когда токен не найден."""

    pass
