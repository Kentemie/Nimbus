from typing import Any, Optional


class NimbusException(Exception):
    """
    Базовый класс для всех специфичных исключений в проекте.
    Позволяет задавать код ошибки и дополнительные детали.
    """

    def __init__(
        self,
        message: str,
        *,
        reason: Optional[Any] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.reason = reason or None
        self.details = details or {}


class RecordAlreadyExistsException(NimbusException):
    def __init__(self, identifier: Optional[int | str] = None):
        message = f"Запись {'с идентификатором ' + identifier if identifier else ''} уже существует."
        super().__init__(message, details={"identifier": identifier})


class RecordNotFoundException(NimbusException):
    def __init__(self, identifier: Optional[int | str] = None):
        message = f"Запись {'с идентификатором ' + str(identifier) if identifier else ''} не найдена."
        super().__init__(message, details={"identifier": identifier})
