from typing import Optional

from .common import NimbusException


class UserException(NimbusException):
    """Базовый класс для исключений, связанных с пользователями."""

    pass


class UserInactiveException(UserException):
    def __init__(self, user_id: Optional[int] = None):
        message = (
            f"Пользователь с ID {user_id} не активен."
            if user_id
            else "Пользователь не активен."
        )
        super().__init__(message, details={"user_id": user_id})


class UserAlreadyVerifiedException(UserException):
    def __init__(self, user_id: Optional[int] = None):
        message = (
            f"Пользователь с ID {user_id} уже верифицирован."
            if user_id
            else "Пользователь уже верифицирован."
        )
        super().__init__(message, details={"user_id": user_id})


class InvalidVerifyTokenException(UserException):
    def __init__(self, token: Optional[str] = None):
        message = (
            f"Неверный или истекший токен верификации: {token}."
            if token
            else "Неверный или истекший токен верификации."
        )
        super().__init__(message, details={"token": token})


class InvalidResetPasswordTokenException(UserException):
    def __init__(self, token: Optional[str] = None):
        message = (
            f"Неверный или истекший токен сброса пароля: {token}."
            if token
            else "Неверный или истекший токен сброса пароля."
        )
        super().__init__(message, details={"token": token})


class InvalidPasswordException(UserException):
    pass
