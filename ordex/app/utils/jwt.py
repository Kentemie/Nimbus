import jwt

from typing import Any

from pydantic import SecretStr


def _get_secret_value(secret: SecretStr) -> str:
    """
    Возвращает строковое значение из объекта SecretStr.

    :param secret: Объект SecretStr.
    :return: Строковое значение секрета.
    """
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return str(secret)


def encode_jwt(
    data: dict,
    secret_key: SecretStr,
    algorithm: str,
) -> str:
    """
    Кодирует данные в JWT-токен.

    :param data: Данные для кодирования.
    :param secret_key: Секретный ключ для подписи токена.
    :param algorithm: Алгоритм подписи.
    :return: Сериализованный JWT-токен.
    """
    payload = data.copy()
    return jwt.encode(
        payload,
        _get_secret_value(secret_key),
        algorithm=algorithm,
    )


def decode_jwt(
    encoded_jwt: str,
    public_key: SecretStr,
    audience: list[str],
    algorithms: list[str],
) -> dict[str, Any]:
    """
    Декодирует JWT-токен и проверяет его подпись.

    :param encoded_jwt: JWT-токен для декодирования.
    :param public_key: Публичный ключ для проверки подписи токена.
    :param audience: Список допустимых значений аудитории токена.
    :param algorithms: Список поддерживаемых алгоритмов подписи.
    :return: Декодированные данные токена.
    """
    return jwt.decode(
        encoded_jwt,
        _get_secret_value(public_key),
        audience=audience,
        algorithms=algorithms,
    )
