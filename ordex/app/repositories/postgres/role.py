from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models import Role


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        stmt = select(Role).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, role_ids: list[int]) -> list[Role]:
        stmt = select(Role).where(Role.id.in_(role_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[Role]:
        stmt = select(Role).where(Role.slug == slug)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(self, create_dict: dict[str, Any]) -> Role:
        role = Role(**create_dict)

        self.session.add(role)

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def update(self, role: Role, update_dict: dict[str, Any]) -> Role:
        for key, value in update_dict.items():
            setattr(role, key, value)

        self.session.add(role)

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)
        await self.session.commit()
