from typing import Any, Optional

from fastapi import Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from domain.exceptions import (
    RecordAlreadyExistsException,
    RecordNotFoundException,
    InvalidPasswordException,
)
from domain.models import User as UserModel
from domain.schemas import UserCreate, UserUpdate

from repositories.postgres import (
    UserRepository,
    RoleRepository,
)
from utils import PasswordHelper


class UserService:
    """
    Сервис для работы с пользователями.

    :param user_repository: Репозиторий пользователей.
    :param role_repository: Репозиторий ролей.
    :param password_helper: Вспомогательный объект для работы с паролями.

    Методы:
    - `get_by_id`: Получение пользователя по ID.
    - `get_by_email`: Получение пользователя по email.
    - `create`: Создание нового пользователя.
    - `update`: Обновление данных пользователя.
    - `delete`: Удаление пользователя.
    - `authenticate`: Аутентификация пользователя по email и паролю.
    - `validate_password`: Проверка сложности пароля.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        password_helper: Optional[PasswordHelper] = None,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository

        if password_helper is None:
            self.password_helper = PasswordHelper()
        else:
            self.password_helper = password_helper

    async def get_by_id(self, user_id: int) -> UserModel:
        """
        Получает пользователя по ID.

        :param user_id: Идентификатор пользователя.
        :return: Модель пользователя.
        :raises RecordNotFoundException: Если пользователь не найден.
        """
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise RecordNotFoundException(user_id)

        return user

    async def get_by_email(self, user_email: str) -> UserModel:
        """
        Получает пользователя по email.

        :param user_email: Email пользователя.
        :return: Модель пользователя.
        :raises RecordNotFoundException: Если пользователь не найден.
        """
        user = await self.user_repository.get_by_email(user_email)

        if user is None:
            raise RecordNotFoundException(user_email)

        return user

    async def create(
        self,
        user_create: UserCreate,
        request: Optional[Request] = None,
    ) -> UserModel:
        """
        Создаёт нового пользователя.

        :param user_create: Данные для создания пользователя.
        :param request: Опциональный объект запроса.
        :return: Созданная модель пользователя.
        :raises RecordAlreadyExistsException: Если пользователь уже существует.
        :raises InvalidPasswordException: Если пароль не соответствует требованиям.
        """
        await self.validate_password(user_create.password)

        existing_user = await self.user_repository.get_by_email(user_create.email)

        if existing_user is not None:
            raise RecordAlreadyExistsException(user_create.email)

        user_dict = user_create.get_create_update_dict()

        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        role_ids = user_dict.pop("role_ids")
        user_dict["roles"] = await self.role_repository.get_by_ids(role_ids)

        created_user = await self.user_repository.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def update(
        self,
        user_update: UserUpdate,
        user: UserModel,
        request: Optional[Request] = None,
    ) -> UserModel:
        """
        Обновляет данные пользователя.

        :param user_update: Данные для обновления пользователя.
        :param user: Модель пользователя для обновления.
        :param request: Опциональный объект запроса.
        :return: Обновлённая модель пользователя.
        """
        user_dict = user_update.get_create_update_dict()

        updated_user = await self._update(user, user_dict)

        await self.on_after_update(updated_user, user_dict, request)

        return updated_user

    async def delete(
        self,
        user: UserModel,
        request: Optional[Request] = None,
    ) -> None:
        """
        Удаляет пользователя.

        :param user: Модель пользователя для удаления.
        :param request: Опциональный объект запроса.
        """
        await self.on_before_delete(user, request)
        await self.user_repository.delete(user)
        await self.on_after_delete(user, request)

    async def request_verify(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        raise NotImplementedError()

    async def verify(self, token: str, request: Optional[Request] = None) -> UserModel:
        raise NotImplementedError()

    async def forgot_password(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        raise NotImplementedError()

    async def reset_password(
        self, token: str, password: str, request: Optional[Request] = None
    ) -> UserModel:
        raise NotImplementedError()

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[UserModel]:
        """
        Аутентифицирует пользователя по его email и паролю.

        :param credentials: Данные для аутентификации (email и пароль).
        :return: Модель пользователя или None, если аутентификация не удалась.
        """
        try:
            user = await self.get_by_email(credentials.username)
        except RecordNotFoundException:
            # Run the hasher to mitigate timing attack
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )

        if not verified:
            return None

        if updated_password_hash is not None:
            await self.user_repository.update(
                user, {"hashed_password": updated_password_hash}
            )

        return user

    async def validate_password(self, password: str) -> None:
        """
        Проверяет, соответствует ли пароль требованиям сложности.

        :param password: Пароль для проверки.
        :raises InvalidPasswordException: Если пароль не соответствует требованиям.
        """
        if not self.password_helper.validate_password(password):
            raise InvalidPasswordException(
                "Пароль слишком простой. Используйте как минимум 12 символов, "
                "большие и маленькие буквы, цифры и специальные символы."
            )

        return

    async def _update(self, user: UserModel, update_dict: dict[str, Any]) -> UserModel:
        """
        Вспомогательный метод для обновления модели пользователя.

        :param user: Модель пользователя для обновления.
        :param update_dict: Данные для обновления пользователя.
        :return: Обновлённая модель пользователя.
        """
        validated_update_dict = {}

        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    raise RecordAlreadyExistsException()
                except RecordNotFoundException:
                    validated_update_dict["email"] = value
                    validated_update_dict["is_verified"] = False
            elif field == "password" and value is not None:
                await self.validate_password(value)
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )
            elif field == "role_ids" and value is not None:
                roles = await self.role_repository.get_by_ids(value)
                validated_update_dict["roles"] = roles
            else:
                validated_update_dict[field] = value

        return await self.user_repository.update(user, validated_update_dict)

    async def on_after_register(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        return

    async def on_after_update(
        self,
        user: UserModel,
        update_dict: dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        return

    async def on_after_request_verify(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ) -> None:
        return

    async def on_after_verify(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        return

    async def on_after_forgot_password(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ) -> None:
        return

    async def on_after_reset_password(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        return

    async def on_after_login(
        self,
        user: UserModel,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        return

    async def on_before_delete(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        return

    async def on_after_delete(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        return
