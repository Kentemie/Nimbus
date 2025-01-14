from domain.exceptions import RecordNotFoundException  # noqa
from domain.models import Role as RoleModel
from domain.schemas import RoleCreate, RoleUpdate
from repositories.postgres import RoleRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    async def get_by_id(self, role_id: int) -> RoleModel:
        role = await self.role_repository.get_by_id(role_id)

        if role is None:
            raise RecordNotFoundException(role_id)

        return role

    async def create(self, role_create: RoleCreate) -> RoleModel:
        return await self.role_repository.create(role_create.get_create_update_dict())

    async def update(self, role_update: RoleUpdate, role: RoleModel) -> RoleModel:
        return await self.role_repository.update(
            role, role_update.get_create_update_dict()
        )

    async def delete(self, role: RoleModel) -> None:
        await self.role_repository.delete(role)
