import jwt

from typing import Any

from pydantic import SecretStr


def _get_secret_value(secret: SecretStr) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()

    return str(secret)


def encode_jwt(
    data: dict,
    secret_key: SecretStr,
    algorithm: str,
) -> str:
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
    return jwt.decode(
        encoded_jwt,
        _get_secret_value(public_key),
        audience=audience,
        algorithms=algorithms,
    )
