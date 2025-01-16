import re

from typing import Any, Callable, Optional, cast, Awaitable, Union
from inspect import Parameter, Signature

from fastapi import Depends, HTTPException, status
from makefun import with_signature

from .service import UserServiceDependency

from core.authentication import AuthenticationBackend
from services import UserService
from domain.models import User as UserModel
from domain.schemas import User as UserSchema
from domain.exceptions import RecordNotFoundException


INVALID_CHARS_PATTERN = re.compile(r"[^0-9a-zA-Z_]")
INVALID_LEADING_CHARS_PATTERN = re.compile(r"^[^a-zA-Z_]+")


def name_to_variable_name(name: str) -> str:
    """
    Преобразует строку имени бэкэнда в строку, безопасную для использования в качестве имени переменной.
    """
    name = re.sub(INVALID_CHARS_PATTERN, "", name)
    name = re.sub(INVALID_LEADING_CHARS_PATTERN, "", name)
    return name


class Authenticator:
    """
    Класс для аутентификации пользователей с использованием заданного бэкенда и сервисов.

    Использует методы аутентификации для получения текущего пользователя по JWT-токену или из базы данных,
    проверяет активность, верификацию и наличие необходимых ролей.

    :param backend: Бэкенд аутентификации, предоставляющий стратегию чтения токенов.
    :param get_user_service: Функция-зависимость для получения экземпляра UserService.
    """

    def __init__(
        self,
        backend: AuthenticationBackend,
        get_user_service: UserServiceDependency,
    ):
        self.backend = backend
        self.get_user_service = get_user_service

    def current_jwt_user(
        self,
        *,
        is_active: bool = False,
        is_verified: bool = False,
        required_roles: Optional[list[str]] = None,
    ) -> Callable[..., Awaitable[tuple[UserSchema, str]]]:
        """
        Создаёт зависимость FastAPI для получения текущего пользователя по JWT-токену.

        :param is_active: Требование, чтобы пользователь был активен.
        :param is_verified: Требование, чтобы пользователь был верифицирован.
        :param required_roles: Список ролей, необходимые для доступа.
        :return: Асинхронная функция-зависимость, возвращающая кортеж из UserSchema и JWT-токена.
        :raises HTTPException:
            - 401 Unauthorized: при отсутствии или недействительности токена, или если пользователь неактивен.
            - 403 Forbidden: если пользователь не верифицирован или не обладает требуемыми ролями.
        """
        signature = self._generate_dependency_signature()

        @with_signature(signature)
        async def _current_jwt_user_dependency(
            *args: Any, **kwargs: Any
        ) -> tuple[UserSchema, str]:
            user, token = await self._authenticate(*args, **kwargs)

            self._check_user_activity_and_verification(
                user=user,
                is_active=is_active,
                is_verified=is_verified,
            )

            self._check_user_roles(
                roles=user.get_role_names(),
                required_roles=required_roles,
            )

            return user, token

        return _current_jwt_user_dependency

    def current_db_user(
        self,
        *,
        is_active: bool = False,
        is_verified: bool = False,
        required_roles: Optional[list[str]] = None,
    ) -> Callable[..., Awaitable[UserModel]]:
        """
        Создаёт зависимость FastAPI для получения текущего пользователя из базы данных.

        :param is_active: Требование, чтобы пользователь был активен.
        :param is_verified: Требование, чтобы пользователь был верифицирован.
        :param required_roles: Список ролей, необходимые для доступа.
        :return: Асинхронная функция-зависимость, возвращающая объект UserModel из базы данных.
        :raises HTTPException:
            - 401 Unauthorized: если JWT недействителен или пользователь не найден.
            - 403 Forbidden: если пользователь не верифицирован или не обладает требуемыми ролями.
        """
        signature = self._generate_dependency_signature(load_db_user=True)

        @with_signature(signature)
        async def _current_db_user_dependency(*args: Any, **kwargs: Any) -> UserModel:
            jwt_user, _ = await self._authenticate(*args, **kwargs)

            user_service: Optional[UserService] = kwargs["user_service"]

            try:
                db_user = await user_service.get_by_id(jwt_user.id)
            except RecordNotFoundException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Пользователь не существует.",
                )

            self._check_user_activity_and_verification(
                user=db_user,
                is_active=is_active,
                is_verified=is_verified,
            )

            self._check_user_roles(
                roles=db_user.get_role_names(),
                required_roles=required_roles,
            )

            return db_user

        return _current_db_user_dependency

    async def _authenticate(
        self,
        *args,  # noqa
        **kwargs,
    ) -> tuple[UserSchema, str]:
        """
        Выполняет аутентификацию пользователя по JWT-токену.

        :param args: Позиционные аргументы зависимости FastAPI.
        :param kwargs: Именованные аргументы, содержащие JWT-токен.
        :return: Кортеж, содержащий UserSchema и JWT-токен.
        :raises HTTPException:
            - 401 Unauthorized: если токен отсутствует, недействителен или просрочен.
        """
        token: Optional[str] = kwargs[name_to_variable_name(self.backend.name)]

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Отсутствует токен или он не валиден.",
            )

        user: Optional[UserSchema] = await self.backend.strategy.read_token(token)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или просроченный токен.",
            )

        return user, token

    def _check_user_activity_and_verification(  # noqa
        self,
        *,
        user: Union[UserSchema, UserModel],
        is_active: bool = False,
        is_verified: bool = False,
    ) -> None:
        """
        Проверяет, активен ли пользователь и прошёл ли он верификацию.

        :param user: Объект пользователя для проверки.
        :param is_active: Требование, чтобы пользователь был активен.
        :param is_verified: Требование, чтобы пользователь был верифицирован.
        :raises HTTPException:
            - 401 Unauthorized: если пользователь неактивен при проверке.
            - 403 Forbidden: если пользователь не верифицирован при проверке.
        """
        if is_active and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь неактивен.",
            )

        if is_verified and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не прошел верификацию.",
            )

    def _check_user_roles(  # noqa
        self,
        *,
        roles: list[str],
        required_roles: Optional[list[str]] = None,
    ) -> None:
        """
        Проверяет, обладает ли пользователь необходимыми ролями.

        :param roles: Список ролей пользователя.
        :param required_roles: Список требуемых ролей.
        :raises HTTPException:
            - 403 Forbidden: если пользователь не обладает одной из требуемых ролей.
        """
        if required_roles:
            for required_role in required_roles:
                if required_role not in roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Вам не разрешено выполнять эту операцию.",
                    )

    def _generate_dependency_signature(self, load_db_user: bool = False) -> Signature:
        """
        Генерирует сигнатуру зависимости FastAPI для аутентификации.

        :param load_db_user: Флаг, указывающий необходимость добавления зависимости для UserService.
        :return: Сигнатура параметров зависимости FastAPI.
        """
        parameters: list[Parameter] = [
            Parameter(
                name=name_to_variable_name(self.backend.name),
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(cast(Callable, self.backend.transport.scheme)),
            ),
        ]

        if load_db_user:
            parameters.append(
                Parameter(
                    name="user_service",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(self.get_user_service),
                ),
            )

        return Signature(parameters)
