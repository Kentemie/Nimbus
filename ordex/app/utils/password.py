import re

from typing import Optional, Union

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class PasswordHelper:
    def __init__(self, password_hash: Optional[PasswordHash] = None) -> None:
        if password_hash is None:
            self.password_hash = PasswordHash((Argon2Hasher(),))
        else:
            self.password_hash = password_hash

        self.complex_password_regex = re.compile(
            r"^"  # начало строки
            r"(?=.*[a-z])"  # хотя бы одна строчная буква
            r"(?=.*[A-Z])"  # хотя бы одна заглавная буква
            r"(?=.*\d)"  # хотя бы одна цифра
            r"(?=.*[@$!%*?&])"  # хотя бы один специальный символ
            r"[^\s]"  # гарантируем отсутствие пробелов
            r"{12,}"  # минимум 12 символов
            r"$"  # конец строки
        )

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, Union[str, None]]:
        return self.password_hash.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.password_hash.hash(password)

    def validate_password(self, password: str) -> bool:
        if not self.complex_password_regex.match(password):
            return False

        return True
