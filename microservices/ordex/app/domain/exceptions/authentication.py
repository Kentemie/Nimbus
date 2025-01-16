from .common import NimbusException


class StrategyDestroyTokenNotSupportedException(NimbusException):
    pass


class JWTStrategyDestroyTokenNotSupportedException(
    StrategyDestroyTokenNotSupportedException
):
    def __init__(self) -> None:
        message = (
            "JWT токен не может быть аннулирован: он действителен до истечения срока."
        )
        super().__init__(message)


class TransportLogoutNotSupportedException(NimbusException):
    def __init__(self):
        message = "Выход через данный транспорт не поддерживается."
        super().__init__(message)
