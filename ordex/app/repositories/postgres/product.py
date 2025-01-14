from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, product_ids: list[int]) -> list[Product]:
        stmt = select(Product).where(Product.id.in_(product_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, create_dict: dict[str, Any]) -> Product:
        product = Product(**create_dict)

        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def update(self, product: Product, update_dict: dict[str, Any]) -> Product:
        for key, value in update_dict.items():
            setattr(product, key, value)

        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)
        await self.session.commit()
