from domain.exceptions import RecordNotFoundException  # noqa
from domain.models import Role as RoleModel
from domain.schemas import RoleCreate, RoleUpdate
from repositories.postgres import RoleRepository


class RoleService:
    """
    Сервис для работы с ролями.

    :param role_repository: Репозиторий ролей.

    Методы:
    - `get_by_id`: Получение роли по ID.
    - `create`: Создание новой роли.
    - `update`: Обновление существующей роли.
    - `delete`: Удаление роли.
    """

    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    async def get_by_id(self, role_id: int) -> RoleModel:
        """
        Получает роль по ID.

        :param role_id: Идентификатор роли.
        :return: Модель роли.
        :raises RecordNotFoundException: Если роль не найдена.
        """
        role = await self.role_repository.get_by_id(role_id)

        if role is None:
            raise RecordNotFoundException(role_id)

        return role

    async def create(self, role_create: RoleCreate) -> RoleModel:
        """
        Создаёт новую роль.

        :param role_create: Данные для создания роли.
        :return: Созданная модель роли.
        """
        return await self.role_repository.create(role_create.get_create_update_dict())

    async def update(self, role_update: RoleUpdate, role: RoleModel) -> RoleModel:
        """
        Обновляет существующую роль.

        :param role_update: Данные для обновления роли.
        :param role: Модель роли для обновления.
        :return: Обновлённая модель роли.
        """
        return await self.role_repository.update(
            role, role_update.get_create_update_dict()
        )

    async def delete(self, role: RoleModel) -> None:
        """
        Удаляет роль.

        :param role: Модель роли для удаления.
        """
        await self.role_repository.delete(role)
